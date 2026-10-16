"""Learner progress: append-only state per character or word, in the attached `progress` database."""

from datetime import datetime, timezone

KINDS = ("character", "word")
STATES = ("unrecognized", "recognized", "mastered")
LABELS = {"unrecognized": "未识", "recognized": "认识", "mastered": "掌握"}
LEARNER = 1  # the app serves learner 1; every row carries learner_id so a second learner is a row, not a redesign


class ProgressError(ValueError):
    """Invalid progress change; the message is Chinese, for the admin page."""


def current(conn, learner_id=LEARNER) -> dict[tuple[str, str], str]:
    """{(kind, key): state} from the latest row per key; keys without a row are unrecognized."""
    sql = """SELECT kind, key, state FROM progress.progress p WHERE learner_id = ?
             AND id = (SELECT max(id) FROM progress.progress WHERE learner_id = p.learner_id AND kind = p.kind AND key = p.key)"""
    return {(r["kind"], r["key"]): r["state"] for r in conn.execute(sql, (learner_id,))}


def state_of(conn, kind, key, learner_id=LEARNER) -> str:
    sql = "SELECT state FROM progress.progress WHERE learner_id = ? AND kind = ? AND key = ? ORDER BY id DESC LIMIT 1"
    row = conn.execute(sql, (learner_id, kind, key)).fetchone()
    return row[0] if row else "unrecognized"


def set_state(conn, kind, key, state, learner_id=LEARNER) -> bool:
    """Append a row unless `state` is already current. Returns whether a row was written."""
    key = (key or "").strip()
    if kind not in KINDS or not key:
        raise ProgressError("没有这个字或词")
    if state not in STATES:
        raise ProgressError("状态只能是 未识、认识 或 掌握")
    if state_of(conn, kind, key, learner_id) == state:
        return False
    changed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sql = "INSERT INTO progress.progress (learner_id, kind, key, state, changed_at) VALUES (?, ?, ?, ?, ?)"
    conn.execute(sql, (learner_id, kind, key, state, changed_at))
    return True
