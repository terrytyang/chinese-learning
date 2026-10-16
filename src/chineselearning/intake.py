"""One-time intake: pre-populate a text's annotations with origin 'auto' (design.md, "Intake")."""

from . import annotations, db
from .annotations import AnnotationError

TABLES = ("text_character", "text_word", "text_expansion", "text_reading", "text_note")


def intake(conn, text_id, data_dir, force=False) -> dict[str, int]:
    """Add every brute-force word match and every character absent from the master; write the file.

    Refuses when the text already has annotations unless `force`, which first
    deletes the rows with origin 'auto' (and only those). Returns rows added.
    """
    text = db.get_text(conn, text_id)
    if text is None:
        raise AnnotationError(f"没有 id 为 {text_id} 的课文")
    existing = sum(conn.execute(f"SELECT count(*) FROM {t} WHERE text_id = ?", (text_id,)).fetchone()[0] for t in TABLES)
    if existing and not force:
        raise AnnotationError(f"课文 {text_id} 已有 {existing} 条标注；加 --force 只重做 auto 部分")
    for t in TABLES:
        conn.execute(f"DELETE FROM {t} WHERE text_id = ? AND origin = 'auto'", (text_id,))
    before = conn.total_changes
    for w in db.find_words(conn, text["body"]):
        annotations.add_word(conn, text_id, w["simplified"], origin="auto")
    words = conn.total_changes - before
    before = conn.total_changes
    for c in db.lookup_characters(conn, db.unique_characters(text["body"])):
        if not c["found"]:
            annotations.add_character(conn, text_id, c["char"], origin="auto")
    characters = conn.total_changes - before
    conn.commit()
    annotations.write_file(conn, text_id, data_dir)
    return {"words": words, "characters": characters}
