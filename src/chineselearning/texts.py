"""Parse the hand-written text files in data/texts/ (format: docs/design.md).

A file is a `key: value` header up to the first blank line, then the body,
verbatim. Any violation raises TextFileError naming the file.
"""

from dataclasses import dataclass
from pathlib import Path

REQUIRED = ("id", "title", "tags")
OPTIONAL = ("author", "period", "notes")


class TextFileError(ValueError):
    """A text file violates the format."""


@dataclass
class Text:
    id: int
    title: str
    tags: list[str]
    body: str
    author: str | None = None
    period: str | None = None
    notes: str | None = None


def parse_text(source: str, name: str = "<text>") -> Text:
    """Parse one file's contents. `name` is used in error messages only."""

    def fail(reason):
        raise TextFileError(f"{name}: {reason}")

    lines = source.split("\n")
    try:
        blank = lines.index("")
    except ValueError:
        fail("no blank line separating header from body")
    header: dict[str, str] = {}
    for line in lines[:blank]:
        key, sep, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not sep or not key:
            fail(f"bad header line {line!r}")
        if key not in REQUIRED + OPTIONAL:
            fail(f"unknown header key {key!r}")
        if key in header:
            fail(f"duplicate header key {key!r}")
        if not value:
            fail(f"empty value for {key!r}")
        header[key] = value
    for key in REQUIRED:
        if key not in header:
            fail(f"missing header key {key!r}")
    try:
        text_id = int(header["id"])
    except ValueError:
        fail(f"id must be an integer, got {header['id']!r}")
    tags = [t.strip() for t in header["tags"].replace("，", ",").split(",")]
    tags = [t for t in tags if t]
    if not tags:
        fail("tags must name at least one category")
    body = "\n".join(lines[blank + 1 :]).removesuffix("\n")
    if not body.strip():
        fail("empty body")
    return Text(
        id=text_id,
        title=header["title"],
        tags=tags,
        body=body,
        author=header.get("author"),
        period=header.get("period"),
        notes=header.get("notes"),
    )


def read_text(path: Path) -> Text:
    return parse_text(path.read_text(encoding="utf-8"), name=str(path))


def load_texts(directory: Path) -> list[Text]:
    """All *.md files in `directory`, in file-name order; ids must be unique."""
    texts = [read_text(p) for p in sorted(Path(directory).glob("*.md"))]
    seen: dict[int, str] = {}
    for text, path in zip(texts, sorted(Path(directory).glob("*.md"))):
        if text.id in seen:
            raise TextFileError(f"{path}: duplicate id {text.id} (also in {seen[text.id]})")
        seen[text.id] = str(path)
    return texts
