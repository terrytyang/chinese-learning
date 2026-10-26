"""One-time intake: facts with origin 'auto' and the default lesson (design.md, "Intake")."""

from . import annotation_files, annotations, db, lesson_files, lessons, pinyin, progress, readings
from .annotations import AnnotationError

FACT_TABLES = ("text_reading", "text_character", "text_word")
TEACHABLE = ("unconfirmed", "exposed")  # the default lesson leaves out what the learner already recognizes or has mastered


def intake(conn, text_id, data_dir, force=False, learner_id=progress.LEARNER) -> dict[str, int]:
    """Add auto words, auto character facts, a reading for every Han position, and the default lesson; write the files.

    A character the master lacks gets pypinyin's reading. Refuses when the text
    already has facts or lessons unless `force`, which redoes only the rows with
    origin 'auto' and leaves lessons alone. The default lesson, "Learn <title>", is
    created only when the text has none; what it selects becomes exposed. Returns rows added.
    """
    text = db.get_text(conn, text_id)
    if text is None:
        raise AnnotationError(f"no text with id {text_id}")
    existing = sum(conn.execute(f"SELECT count(*) FROM {t} WHERE text_id = ?", (text_id,)).fetchone()[0] for t in FACT_TABLES)
    existing += len(lessons.for_text(conn, text_id))
    if existing and not force:
        raise AnnotationError(f"text {text_id} already has {existing} facts or lessons; --force redoes the auto rows only")
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
        reading = r["pinyin"] or pinyin.guess(r["char"])
        if r["source"] != "stored" and reading:
            annotations.set_reading(conn, text_id, r["position"], r["char"], reading, "auto")
    done("readings")
    counts["lesson"] = None
    if not lessons.for_text(conn, text_id):
        states = progress.current(conn, learner_id)
        counts["lesson"] = lesson_id = lessons.create(conn, text_id, f"Learn {text['title']}")
        for ch in db.unique_characters(text["body"]):
            if states.get(("character", ch), "unconfirmed") in TEACHABLE:
                lessons.add_character(conn, lesson_id, ch)
                progress.expose(conn, "character", ch, learner_id)
        for row in conn.execute("SELECT surface FROM text_word WHERE text_id = ?", (text_id,)).fetchall():
            if states.get(("word", row[0]), "unconfirmed") in TEACHABLE:
                lessons.add_word(conn, lesson_id, row[0])
                progress.expose(conn, "word", row[0], learner_id)
    conn.commit()
    annotation_files.write_file(conn, text_id, data_dir)
    lesson_files.write_files(conn, text_id, data_dir)
    return counts
