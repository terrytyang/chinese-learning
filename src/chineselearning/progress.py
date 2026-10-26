"""Learner progress: one row per character or word with its current state, in the attached `progress` database."""

from datetime import datetime, timezone

KINDS = ("character", "word")
STATES = ("unconfirmed", "exposed", "recognized", "mastered")
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


def set_state(conn, kind, key, state, learner_id=LEARNER) -> bool:
    """Upsert the row; `unconfirmed` deletes it. Returns whether anything changed."""
    key = (key or "").strip()
    if kind not in KINDS or not key:
        raise ProgressError("no such character or word")
    if kind == "word" and len(key) == 1:
        raise ProgressError(SINGLE_CHARACTER)
    if state not in STATES:
        raise ProgressError("state must be unconfirmed, exposed, recognized or mastered")
    if state_of(conn, kind, key, learner_id) == state:
        return False
    if state == "unconfirmed":
        conn.execute("DELETE FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ?", (learner_id, kind, key))
        return True
    changed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sql = """INSERT INTO progress.progress (learner_id, kind, key, state, changed_at) VALUES (?, ?, ?, ?, ?)
             ON CONFLICT (learner_id, kind, key) DO UPDATE SET state = excluded.state, changed_at = excluded.changed_at"""
    conn.execute(sql, (learner_id, kind, key, state, changed_at))
    return True


def expose(conn, kind, key, learner_id=LEARNER) -> bool:
    """Adding to a lesson: unconfirmed becomes exposed; every other state stays."""
    return state_of(conn, kind, key, learner_id) == "unconfirmed" and set_state(conn, kind, key, "exposed", learner_id)
