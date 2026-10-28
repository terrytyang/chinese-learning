"""Learner progress: one row per character or word with its current state, in the attached `progress` database."""

from datetime import datetime, timezone

KINDS = ("character", "word")
STATES = ("unconfirmed", "exposed", "recognized", "mastered")
ORIGINS = ("auto", "manual", "import")  # intake or adding to a lesson; a page; a file
LEARNER = 1  # the app serves learner 1; every row carries learner_id so a second learner is a row, not a redesign
SINGLE_CHARACTER = "a single character is a character; add it in Characters"


class ProgressError(ValueError):
    """Invalid progress change; the message is for the admin page."""


def current(conn, learner_id=LEARNER) -> dict[tuple[str, str], str]:
    """{(kind, key): state}; keys without a row are unconfirmed."""
    sql = "SELECT kind, key, state FROM progress.progress WHERE learner_id = ?"
    return {(r["kind"], r["key"]): r["state"] for r in conn.execute(sql, (learner_id,))}


def state_of(conn, kind, key, learner_id=LEARNER) -> str:
    row = conn.execute("SELECT state FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ?", (learner_id, kind, key)).fetchone()
    return row[0] if row else "unconfirmed"


def set_state(conn, kind, key, state, origin, learner_id=LEARNER, changed_at=None) -> bool:
    """Upsert the row with its origin; `unconfirmed` deletes it. Returns whether anything changed.

    `changed_at` defaults to now (an import passes the file's date). A row already in `state` with the same origin is left as
    it is; with another origin, its origin and date change (a page click on the lit button turns an `auto` row `manual`).
    """
    key = (key or "").strip()
    if kind not in KINDS or not key:
        raise ProgressError("no such character or word")
    if kind == "word" and len(key) == 1:
        raise ProgressError(SINGLE_CHARACTER)
    if state not in STATES:
        raise ProgressError("state must be unconfirmed, exposed, recognized or mastered")
    if origin not in ORIGINS:
        raise ProgressError("origin must be auto, manual or import")
    row = conn.execute("SELECT state, origin FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ?", (learner_id, kind, key)).fetchone()
    if (row[0] if row else "unconfirmed") == state and (row is None or row[1] == origin):
        return False
    if state == "unconfirmed":
        conn.execute("DELETE FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ?", (learner_id, kind, key))
        return True
    changed_at = changed_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sql = """INSERT INTO progress.progress (learner_id, kind, key, state, changed_at, origin) VALUES (?, ?, ?, ?, ?, ?)
             ON CONFLICT (learner_id, kind, key) DO UPDATE SET state = excluded.state, changed_at = excluded.changed_at, origin = excluded.origin"""
    conn.execute(sql, (learner_id, kind, key, state, changed_at, origin))
    return True


def expose(conn, kind, key, learner_id=LEARNER) -> bool:
    """Adding to a lesson: unconfirmed becomes exposed (origin `auto`); every other state stays."""
    return state_of(conn, kind, key, learner_id) == "unconfirmed" and set_state(conn, kind, key, "exposed", "auto", learner_id)


def release(conn, kind, key, learner_id=LEARNER) -> bool:
    """Removing from the last lesson that held it: an automatic `exposed` goes back to unconfirmed; anything else stays."""
    row = conn.execute("SELECT 1 FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ? AND state = 'exposed' AND origin = 'auto'", (learner_id, kind, key)).fetchone()
    return bool(row) and set_state(conn, kind, key, "unconfirmed", "auto", learner_id)
