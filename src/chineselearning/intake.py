"""One-time intake: facts with origin 'auto' and the default lesson (design.md, "Intake")."""

from pathlib import Path

from . import annotation_files, annotations, db, lesson_files, lessons, progress, readings
from .annotations import AnnotationError

FACT_TABLES = ("text_reading", "text_character", "text_word")
TEACHABLE = ("unconfirmed", "exposed")  # the default lesson leaves out what the learner already recognizes or has mastered


def new_texts(conn) -> list[int]:
    """Ids of the texts with no facts and no lesson, in id order."""
    absent = " UNION ".join(f"SELECT text_id FROM {t}" for t in FACT_TABLES + ("lesson",))
    return [r[0] for r in conn.execute(f"SELECT id FROM text WHERE id NOT IN ({absent}) ORDER BY id")]


def intake(conn, text_id, data_dir, force=False, learner_id=progress.LEARNER) -> dict[str, int]:
    """Add auto words, a reading for every Han position, and the default lesson; write the files.

    Every character of the text must be in the dictionary (HSK or supplement). Refuses when the
    text already has facts or lessons unless `force`, which redoes only the rows with origin 'auto'
    and leaves lessons alone. The default lesson, "Learn <title>", is created only when the text has
    none; what it selects becomes exposed. Returns rows added.
    """
    text = db.get_text(conn, text_id)
    if text is None:
        raise AnnotationError(f"no text with id {text_id}")
    missing = [c["char"] for c in db.lookup_characters(conn, db.unique_characters(text["body"])) if not c["found"]]
    if missing:
        raise AnnotationError(f"text {text_id} has characters not in the dictionary: {', '.join(missing)}; add them to data/supplement.tsv")
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
    for r in readings.resolve(conn, text_id):  # stored (manual/suggested) rows win; the rest are persisted now
        if r["source"] != "stored":
            annotations.set_reading(conn, text_id, r["position"], r["char"], r["pinyin"], "auto")
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


def reset_plan(conn, text_id, data_dir) -> dict:
    """What `reset` would delete: {table: rows} for the fact tables, `lessons`, and `files` (the annotation and lesson files that exist)."""
    if db.get_text(conn, text_id) is None:
        raise AnnotationError(f"no text with id {text_id}")
    plan = {t: conn.execute(f"SELECT count(*) FROM {t} WHERE text_id = ?", (text_id,)).fetchone()[0] for t in FACT_TABLES}
    plan["lessons"] = len(lessons.for_text(conn, text_id))
    files = [annotation_files.file_path(data_dir, text_id)] + sorted(Path(data_dir, "lessons").glob(f"{text_id}-*.json"))
    plan["files"] = [p for p in files if p.is_file()]
    return plan


def reset(conn, text_id, data_dir) -> dict:
    """Delete every fact and lesson of the text, manual and suggested rows included, and their files; progress is untouched.
    Returns the plan it carried out. The caller runs `intake` next."""
    plan = reset_plan(conn, text_id, data_dir)
    for t in FACT_TABLES + ("lesson",):  # the lesson tables cascade
        conn.execute(f"DELETE FROM {t} WHERE text_id = ?", (text_id,))
    conn.commit()
    for path in plan["files"]:
        path.unlink()
    return plan
