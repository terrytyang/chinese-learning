"""Progress import (design.md, layer 4): resolve each item's state from the standard files and the current rows, add unmatched
items to the supplement, write the states with `changed_at = as_of`, and report."""

from dataclasses import dataclass, field
from pathlib import Path

from . import db, progress, progress_files, supplement
from .progress import LEARNER, STATES
from .progress_files import ProgressFileError

RANK = {s: i for i, s in enumerate(STATES)}


@dataclass
class Candidate:
    state: str
    as_of: str
    origin: str
    why: str


def candidates(conn, entries, learner_id=LEARNER) -> dict[tuple[str, str], list[Candidate]]:
    """Per (kind, key): the explicit entries, for a character every entry of a word containing it (with the word's origin), and
    the current row (with its own)."""
    out: dict[tuple[str, str], list[Candidate]] = {}
    for e in entries:
        out.setdefault((e.kind, e.item), [])
        if e.state is None:
            continue
        out[(e.kind, e.item)].append(Candidate(e.state, e.as_of, e.origin, f"{e.state} {e.as_of} in {e.where}, origin {e.origin}"))
        if e.kind == "word":
            for ch in dict.fromkeys(e.item):
                out.setdefault(("character", ch), []).append(Candidate(e.state, e.as_of, e.origin, f"{e.state} {e.as_of} implied by {e.item} in {e.where}, origin {e.origin}"))
    for (kind, key), found in out.items():
        row = conn.execute("SELECT state, changed_at, origin FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ?", (learner_id, kind, key)).fetchone()
        if row:
            found.append(Candidate(row[0], row[1][:10], row[2], f"{row[0]} {row[1][:10]} current, origin {row[2]}"))
    return out


def resolve(conn, entries, learner_id=LEARNER) -> dict[tuple[str, str], tuple[str, str, str, str]]:
    """{(kind, key): (state, as_of, origin, why)}: `auto` candidates count only when no other kind exists; among the rest the
    latest wins, the lowest state on a tie. Items with no candidate are absent."""
    out = {}
    for item, found in candidates(conn, entries, learner_id).items():
        considered = [c for c in found if c.origin != "auto"] or found
        if considered:
            best = max(considered, key=lambda c: (c.as_of, -RANK[c.state]))
            out[item] = (best.state, best.as_of, best.origin, best.why)
    return out


def unmatched(conn, entries) -> list[dict]:
    """One record per item the dictionary lacks, in order of first appearance, with the first pinyin, gloss and level any entry gives.

    Characters come first so that a word's characters exist before the word; a word with a character in neither the
    dictionary nor the files is a ProgressFileError.
    """
    seen, records = {}, []
    for e in entries:
        if e.item not in seen:
            lookup = db.lookup_character if e.kind == "character" else db.lookup_word
            seen[e.item] = None if lookup(conn, e.item) else {"item": e.item, "pinyin": "", "gloss": "", "level": "", "where": e.where}
            if seen[e.item]:
                records.append(seen[e.item])
        if seen[e.item]:
            for key in ("pinyin", "gloss", "level"):
                seen[e.item][key] = seen[e.item][key] or getattr(e, key)
    chars = {r["item"] for r in records if len(r["item"]) == 1}
    for r in records:
        missing = [ch for ch in dict.fromkeys(r["item"]) if len(r["item"]) > 1 and ch not in chars and db.lookup_character(conn, ch) is None]
        if missing:
            raise ProgressFileError(f"{r['where']}: “{r['item']}” has characters not in the dictionary: {', '.join(missing)}; add them to the file or data/supplement.tsv")
    return sorted(records, key=lambda r: len(r["item"]) > 1)


@dataclass
class Report:
    check: bool
    files: list[str]
    entries: int
    conversions: list[tuple[str, str]] = field(default_factory=list)  # (original, simplified)
    changes: dict[str, list[str]] = field(default_factory=dict)  # "unconfirmed→exposed" -> keys
    unchanged: int = 0
    downgrades: list[str] = field(default_factory=list)
    added: list[dict] = field(default_factory=list)  # the supplement records

    def text(self) -> str:
        lines = [("check: nothing written; " if self.check else "") + "files read: " + (", ".join(self.files) or "none")]
        converted = f", converted from traditional: {', '.join(f'{a}→{b}' for a, b in self.conversions)}" if self.conversions else ""
        lines.append(f"entries: {self.entries}{converted}")
        lines += [f"{transition}: {', '.join(keys)}" for transition, keys in self.changes.items()]
        lines.append(f"unchanged: {self.unchanged}")
        if self.downgrades:
            lines.append("downgrades: " + "; ".join(self.downgrades))
        if self.added:
            unglossed = sum(1 for r in self.added if not r["gloss"])
            lines.append(f"{'would add' if self.check else 'added'} to supplement: {', '.join(r['item'] for r in self.added)} ({unglossed} without a gloss)")
        return "\n".join(lines)


def default_files(data_dir) -> list[Path]:
    """The exported snapshot, then every batch under data/import/progress/."""
    data_dir = Path(data_dir)
    return sorted((data_dir / "progress").glob("*.tsv")) + sorted((data_dir / "import" / "progress").glob("*.tsv"))


def run(conn, data_dir, files=None, check=False, learner_id=LEARNER) -> Report:
    """Read the files (all of them before anything is written), resolve, add to the supplement, write the states, and report."""
    paths = [Path(f) for f in files] if files else default_files(data_dir)
    entries = []
    for path in paths:
        if not path.is_file():
            raise ProgressFileError(f"{path}: no such file")
        entries += progress_files.read(path)
    missing = unmatched(conn, entries)
    report = Report(check, [str(p) for p in paths], len(entries), [(e.original, e.item) for e in entries if e.original], added=missing)
    for (kind, key), (state, as_of, origin, why) in resolve(conn, entries, learner_id).items():
        current = progress.state_of(conn, kind, key, learner_id)
        if current == state:
            report.unchanged += 1
            continue
        report.changes.setdefault(f"{current}→{state}", []).append(key)
        if RANK[state] < RANK[current]:
            report.downgrades.append(f"{key} {current}→{state} ({why})")
        if not check:
            progress.set_state(conn, kind, key, state, origin, learner_id, changed_at=as_of)
    if not check:
        for r in missing:
            supplement.add(conn, data_dir, r["item"], r["pinyin"], r["gloss"], r["level"])
        conn.commit()
    return report
