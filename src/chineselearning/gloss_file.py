"""data/character-gloss.tsv: the curated gloss of every HSK character (design.md, layer 2).

The derivation bakes the file into hsk.sql; `apply` runs at build after hsk.sql so that `update`, the dictionary page's
edit of an HSK character's gloss, can rewrite one line without regenerating the master. A line is `char  gloss` (one
tab); `#` starts a comment. A gloss is non-empty with no tab or newline; the prompt's style rules are not enforced.
"""

from pathlib import Path

from . import drift

FILE = "character-gloss.tsv"


class GlossFileError(ValueError):
    """An invalid line or gloss; at load the message starts with the file and line."""


def file_path(data_dir) -> Path:
    return Path(data_dir) / FILE


def clean(gloss) -> str:
    gloss = (gloss or "").strip()
    if not gloss:
        raise GlossFileError("a gloss is required")
    if "\t" in gloss or "\n" in gloss:
        raise GlossFileError("a gloss is one line without tabs")
    return gloss


def read(data_dir) -> list[tuple[int, str, str]]:
    """(line number, character, gloss) for every data line; a malformed line is a GlossFileError naming it."""
    path, out = file_path(data_dir), []
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 2 or len(fields[0]) != 1:
            raise GlossFileError(f"{path}:{number}: expected one character, a tab and its gloss")
        try:
            out.append((number, fields[0], clean(fields[1])))
        except GlossFileError as e:
            raise GlossFileError(f"{path}:{number}: {e}") from None
    return out


def apply(conn, data_dir) -> int:
    """Set every listed character's gloss; a character the master lacks is an error naming the line. Returns the lines applied."""
    path = file_path(data_dir)
    if not path.is_file():
        return 0
    lines = read(data_dir)
    for number, char, gloss in lines:
        if conn.execute("UPDATE character SET gloss = ? WHERE char = ?", (gloss, char)).rowcount == 0:
            raise GlossFileError(f"{path}:{number}: “{char}” is not in the HSK master")
    return len(lines)


def update(conn, data_dir, char, gloss):
    """Rewrite one HSK character's line in place (the rest of the file byte-identical) and its row."""
    gloss = clean(gloss)
    row = conn.execute("SELECT source FROM character WHERE char = ?", (char,)).fetchone()
    if row is None or row[0] != "hsk":
        raise GlossFileError(f"“{char}” is not an HSK character")
    path = file_path(data_dir)
    lines = path.read_text(encoding="utf-8").split("\n")
    at = next((i for i, line in enumerate(lines) if not line.startswith("#") and line.split("\t")[0] == char), None)
    if at is None:
        raise GlossFileError(f"“{char}” is not in data/{FILE}")
    conn.execute("UPDATE character SET gloss = ? WHERE char = ?", (gloss, char))
    lines[at] = f"{char}\t{gloss}"
    path.write_text("\n".join(lines), encoding="utf-8")
    drift.touch(conn, data_dir, path)
