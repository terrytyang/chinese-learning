"""Read-only historical source access shared by the explicit data tools."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3


@contextmanager
def open_source(path):
    source = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        source.execute("PRAGMA query_only = ON")
        source.execute("BEGIN")  # One consistent snapshot for all extraction queries.
        yield source
    finally:
        source.close()


def traditional_candidate(source, char):
    """Prefer standalone entries, then shorter words; retain the first form only.

    Compounds supply a positional candidate only when both forms have equal
    code-point lengths. This is a best-effort reference, not a conversion engine.
    """
    rows = source.execute(
        """SELECT e.simplified, c.position, f.traditional
           FROM hsk_entry_char c
           JOIN hsk_entry e USING (entry_id)
           JOIN hsk_form f USING (entry_id)
           WHERE c.char = ? AND length(e.simplified) = length(f.traditional)
           ORDER BY length(e.simplified), e.entry_id, f.form_seq, c.position""",
        (char,),
    )
    row = rows.fetchone()
    return row[2][row[1] - 1] if row else None

