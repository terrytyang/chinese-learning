"""The data/ drift guard (design.md, 2026-10-28): `build` records every file's path, size and mtime in the content database's
`meta` table; the admin shell compares the tree on each render and shows a banner naming the changed files; the writers the
app has update the record for the files they wrote, so the banner appears only for changes made outside the app."""

import json
import os
from pathlib import Path

KEY = "data_fingerprint"
MESSAGE = "data/ has changed since the last build ({}): run `chineselearning build`"


def fingerprint(data_dir) -> dict[str, list[int]]:
    """{relative path: [size, mtime in ns]} for every file under data/."""
    data_dir = Path(data_dir)
    out = {}
    for path in sorted(p for p in data_dir.rglob("*") if p.is_file()):
        st = path.stat()
        out[path.relative_to(data_dir).as_posix()] = [st.st_size, st.st_mtime_ns]
    return out


def stored(conn) -> dict[str, list[int]] | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (KEY,)).fetchone()
    return json.loads(row[0]) if row else None


def store(conn, data_dir, record=None):
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (KEY, json.dumps(record if record is not None else fingerprint(data_dir))))


def changed(conn, data_dir) -> list[str]:
    """The files that differ from the record (changed, added or removed), relative to data/, sorted; [] when nothing has."""
    record = stored(conn)
    if record is None:
        return []
    current = fingerprint(data_dir)
    return sorted(path for path in set(record) | set(current) if record.get(path) != current.get(path))


def touch(conn, data_dir, *paths):
    """Update the record for files the app has just written or removed. Writers call this after their file write, which is
    often after the caller's commit: when the connection is idle the update is committed here, otherwise it rides the open
    transaction."""
    record = stored(conn)
    if record is None:
        return
    data_dir = Path(data_dir).resolve()
    for path in paths:
        path = Path(path).resolve()
        key = path.relative_to(data_dir).as_posix()
        if path.is_file():
            st = os.stat(path)
            record[key] = [st.st_size, st.st_mtime_ns]
        else:
            record.pop(key, None)
    idle = not conn.in_transaction
    store(conn, data_dir, record)
    if idle:
        conn.commit()


def message(files) -> str:
    return MESSAGE.format(", ".join(files))
