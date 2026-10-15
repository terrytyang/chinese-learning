"""Read-only library queries, independent of HTTP and template rendering."""

from sqlalchemy import inspect, select

from chineselearning.schema import library_text, text_category

METADATA_COLUMNS = (
    library_text.c.id, library_text.c.title, library_text.c.author,
    library_text.c.period, text_category.c.label.label("category_label"),
)


def list_texts(engine):
    """Order by explicit ID; pre-library databases have an empty library."""
    with engine.connect() as connection:
        if not inspect(connection).has_table(library_text.name):
            return []
        statement = (select(*METADATA_COLUMNS).select_from(library_text.join(text_category))
                     .order_by(library_text.c.id))
        return [dict(row) for row in connection.execute(statement).mappings()]


def get_text(engine, text_id):
    if not 1 <= text_id <= 2**63 - 1:
        return None
    with engine.connect() as connection:
        if not inspect(connection).has_table(library_text.name):
            return None
        statement = (select(*METADATA_COLUMNS, library_text.c.body)
                     .select_from(library_text.join(text_category))
                     .where(library_text.c.id == text_id))
        row = connection.execute(statement).mappings().first()
        return dict(row) if row is not None else None
