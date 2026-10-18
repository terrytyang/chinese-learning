"""One-time intake: facts with origin 'auto' and the default lesson (design.md, "Intake")."""

from . import annotation_files, annotations, db, lesson_files, lessons, progress, readings
from .annotations import AnnotationError

FACT_TABLES = ("text_reading", "text_character", "text_word")


def intake(conn, text_id, data_dir, force=False, learner_id=progress.LEARNER) -> dict[str, int]:
    """Add auto words, auto character facts, a reading for every Han position, and the default lesson; write the files.

    Refuses when the text already has facts or lessons unless `force`, which
    redoes only the rows with origin 'auto' and leaves lessons alone. The default
    lesson is created only when the text has none. Returns rows added.
    """
    text = db.get_text(conn, text_id)
    if text is None:
        raise AnnotationError(f"没有 id 为 {text_id} 的课文")
    existing = sum(conn.execute(f"SELECT count(*) FROM {t} WHERE text_id = ?", (text_id,)).fetchone()[0] for t in FACT_TABLES)
    existing += len(lessons.for_text(conn, text_id))
    if existing and not force:
        raise AnnotationError(f"课文 {text_id} 已有 {existing} 条标注或课程；加 --force 只重做 auto 部分")
    for t in FACT_TABLES:
        conn.execute(f"DELETE FROM {t} WHERE text_id = ? AND origin = 'auto'", (text_id,))
    counts, before = {}, conn.total_changes

    def done(key):
        nonlocal before
        counts[key], before = conn.total_changes - before, conn.total_changes

    for w in db.find_words(conn, text["body"]):
        annotations.add_word(conn, text_id, w["simplified"], origin="auto")
    done("words")
    for c in db.lookup_characters(conn, db.unique_characters(text["body"])):
        if not c["found"]:
            annotations.add_character(conn, text_id, c["char"], origin="auto")
    done("characters")
    for r in readings.resolve(conn, text_id):  # stored (manual/suggested) rows win; the rest are persisted now
        if r["source"] != "stored" and r["pinyin"]:
            annotations.set_reading(conn, text_id, r["position"], r["char"], r["pinyin"], "auto")
    done("readings")
    counts["lesson"] = None
    if not lessons.for_text(conn, text_id):
        states = progress.current(conn, learner_id)
        counts["lesson"] = lesson_id = lessons.create(conn, text_id, text["title"])
        for ch in db.unique_characters(text["body"]):
            if states.get(("character", ch)) != "mastered":
                lessons.add_character(conn, lesson_id, ch)
        for row in conn.execute("SELECT surface FROM text_word WHERE text_id = ?", (text_id,)).fetchall():
            lessons.add_word(conn, lesson_id, row[0])
    conn.commit()
    annotation_files.write_file(conn, text_id, data_dir)
    lesson_files.write_files(conn, text_id, data_dir)
    return counts
