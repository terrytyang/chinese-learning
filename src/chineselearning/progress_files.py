"""Standard progress files (format: data/import/progress/README.md): read one, and write the learner's snapshot to data/progress/."""

import re
from dataclasses import dataclass
from pathlib import Path

from opencc import OpenCC

from .progress import LEARNER, ORIGINS, STATES

COLUMNS = ("item", "state", "as_of", "pinyin", "gloss", "level", "origin")
REQUIRED = COLUMNS[:3]  # the column header names these, then any of the rest in this order
HEADER_KEYS = ("source", "as_of", "state")
LINE_STATES = STATES[1:]  # a file never says "unconfirmed"
DATE = re.compile(r"\d{4}-\d\d-\d\d")
_T2S = OpenCC("t2s")


class ProgressFileError(ValueError):
    """A standard file violates the format; the message names the file and line."""


@dataclass
class Entry:
    item: str  # simplified
    state: str | None  # None: the file says nothing about the student
    as_of: str  # YYYY-MM-DD
    pinyin: str
    gloss: str
    level: str
    origin: str  # auto | manual | import (blank in the file = import)
    file: str  # the file's name, for the report
    line: int
    original: str | None = None  # the traditional form the item was converted from

    @property
    def kind(self) -> str:
        return "character" if len(self.item) == 1 else "word"

    @property
    def where(self) -> str:
        return f"{self.file}:{self.line}"


def read(path) -> list[Entry]:
    """Every data line of a standard file; header values fill blank columns. Any violation is a ProgressFileError naming the line."""
    path, header, entries, columns = Path(path), {}, [], None
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        where = f"{path}:{number}"
        if "?" in line:
            raise ProgressFileError(f"{where}: “?” must be replaced by the owner before import")
        if not line.strip():
            continue
        if line.startswith("#"):
            key, sep, value = line[1:].partition(":")
            key, value = key.strip(), value.strip()
            if columns or not sep or key not in HEADER_KEYS:
                raise ProgressFileError(f"{where}: unknown header line {line!r}")
            if key == "as_of" and not DATE.fullmatch(value):
                raise ProgressFileError(f"{where}: as_of must be a date (YYYY-MM-DD), not “{value}”")
            if key == "state" and value not in LINE_STATES + ("none",):
                raise ProgressFileError(f"{where}: state must be exposed, recognized, mastered or none, not “{value}”")
            header[key] = value
            continue
        fields = [f.strip() for f in line.split("\t")]
        if columns is None:
            rest = [c for c in COLUMNS[3:] if c in fields]
            if fields != list(REQUIRED) + rest:
                raise ProgressFileError(f"{where}: expected the column header: {' '.join(REQUIRED)}, then any of {' '.join(COLUMNS[3:])} in that order")
            columns = fields
            continue
        values = dict(zip(columns, fields + [""] * len(columns)))
        item, state, as_of, pinyin, gloss, level, origin = (values.get(c, "") for c in COLUMNS)
        if not item:
            raise ProgressFileError(f"{where}: blank item")
        if state and state not in LINE_STATES:
            raise ProgressFileError(f"{where}: state must be exposed, recognized or mastered, not “{state}”")
        state = state or header.get("state", "none")
        as_of = as_of or header.get("as_of", "")
        if not as_of:
            raise ProgressFileError(f"{where}: no as_of on the line or in the header")
        if not DATE.fullmatch(as_of):
            raise ProgressFileError(f"{where}: as_of must be a date (YYYY-MM-DD), not “{as_of}”")
        if level and (not level.isdigit() or not 1 <= int(level) <= 7):
            raise ProgressFileError(f"{where}: level must be 1 to 7, not “{level}”")
        if origin and origin not in ORIGINS:
            raise ProgressFileError(f"{where}: origin must be auto, manual or import, not “{origin}”")
        simplified = _T2S.convert(item)
        entries.append(Entry(simplified, None if state == "none" else state, as_of, pinyin, gloss, level, origin or "import", path.name, number, item if simplified != item else None))
    if columns is None:
        raise ProgressFileError(f"{path}: no column header")
    return entries


def slug(name) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "learner"


def export(conn, data_dir, learner_id=LEARNER) -> Path:
    """Write data/progress/<learner slug>.tsv: `item state as_of origin` by key, as_of being the date part of changed_at."""
    row = conn.execute("SELECT name FROM progress.learner WHERE id = ?", (learner_id,)).fetchone()
    if row is None:
        raise ProgressFileError(f"no learner with id {learner_id}")
    rows = conn.execute("SELECT key, state, substr(changed_at, 1, 10), origin FROM progress.progress WHERE learner_id = ? ORDER BY key", (learner_id,))
    path = Path(data_dir) / "progress" / f"{slug(row[0])}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# source: export\nitem\tstate\tas_of\torigin\n" + "".join(f"{key}\t{state}\t{date}\t{origin}\n" for key, state, date, origin in rows), encoding="utf-8")
    return path
