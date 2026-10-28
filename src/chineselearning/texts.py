"""Parse the hand-written text files in data/texts/ (format: docs/design.md).

A file is a `key: value` header up to the first blank line, then the body,
verbatim. Any violation raises TextFileError naming the file.
"""

import re
from dataclasses import dataclass
from pathlib import Path

# Han characters (CJK unified ideographs incl. extensions, compatibility, 〇) and maximal runs of them.
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U000323af\u3007]")
HAN_RUN = re.compile(HAN.pattern + "+")

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


def file_name(text_id, title) -> str:
    """The file a new text is written to: three-digit id, the title."""
    return f"{text_id:03d}-{title.strip()}.md"


def compose(text_id, title, tags, body, author="", period="") -> str:
    """The content of a new text file: header lines in the order id, title, author, period, tags (empty optionals
    omitted), a blank line, the body as typed with each line's trailing whitespace stripped and one trailing newline.
    Not validated here; `parse_text` is the rule."""
    lines = [f"id: {text_id}", f"title: {title.strip()}"]
    lines += [f"{key}: {value.strip()}" for key, value in (("author", author), ("period", period)) if value.strip()]
    lines.append(f"tags: {tags.strip()}")
    body = "\n".join(line.rstrip() for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    return "\n".join(lines) + "\n\n" + body.rstrip("\n") + "\n"


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


def path_for(directory, text_id) -> Path:
    """The file in `directory` whose header carries `text_id`."""
    for path in sorted(Path(directory).glob("*.md")):
        if read_text(path).id == text_id:
            return path
    raise TextFileError(f"no text file with id {text_id} in {directory}")


def write_header(path, **updates) -> Text:
    """Rewrite header values in place; the body and every other header line stay byte-for-byte.

    A blank value removes an optional key. The result is validated like any text file before writing.
    """
    source = Path(path).read_text(encoding="utf-8")
    head, sep, body = source.partition("\n\n")
    if not sep:
        raise TextFileError(f"{path}: no blank line separating header from body")
    lines = head.split("\n")
    for key, value in updates.items():
        value = (value or "").strip()
        index = next((i for i, line in enumerate(lines) if line.partition(":")[0].strip() == key), None)
        if value and index is None:
            lines.append(f"{key}: {value}")
        elif value:
            lines[index] = f"{key}: {value}"
        elif index is not None:
            del lines[index]
    rewritten = "\n".join(lines) + sep + body
    text = parse_text(rewritten, name=str(path))
    Path(path).write_text(rewritten, encoding="utf-8")
    return text
