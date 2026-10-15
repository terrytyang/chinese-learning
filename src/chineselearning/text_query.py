"""Read-only library queries, independent of HTTP and template rendering."""

import re

from sqlalchemy import inspect, select

from chineselearning.schema import library_text, text_category, text_category_assignment

METADATA_COLUMNS = (
    library_text.c.id, library_text.c.title, library_text.c.author, library_text.c.period,
)


def parse_category_filter(value):
    if value is None or value == "":
        return None
    if not re.fullmatch(r"[0-9]+", value) or len(value) > 19:
        raise ValueError("category_id must be a positive 64-bit integer or empty")
    category_id = int(value)
    if not 1 <= category_id <= 2**63 - 1:
        raise ValueError("category_id must be a positive 64-bit integer or empty")
    return category_id


def add_categories(connection, records):
    """Fetch all labels in one query, preserving category-ID order per text."""
    if not records:
        return records
    by_id = {record["id"]: record for record in records}
    for record in records:
        record["categories"] = []
    statement = (select(text_category_assignment.c.text_id, text_category.c.id, text_category.c.label)
                 .select_from(text_category_assignment.join(text_category))
                 .where(text_category_assignment.c.text_id.in_(by_id))
                 .order_by(text_category_assignment.c.text_id, text_category.c.id))
    for text_id, category_id, label in connection.execute(statement):
        by_id[text_id]["categories"].append(dict(id=category_id, label=label))
    return records


def list_texts(engine, *, category_id=None, author=None, period=None):
    """Use EXISTS for categories so each text occurs once, ordered by explicit ID."""
    with engine.connect() as connection:
        if not inspect(connection).has_table(library_text.name):
            return []
        statement = select(*METADATA_COLUMNS).order_by(library_text.c.id)
        if category_id is not None:
            assigned = select(text_category_assignment.c.text_id).where(
                text_category_assignment.c.text_id == library_text.c.id,
                text_category_assignment.c.category_id == category_id,
            ).exists()
            statement = statement.where(assigned)
        if author:
            statement = statement.where(library_text.c.author == author)
        if period:
            statement = statement.where(library_text.c.period == period)
        records = [dict(row) for row in connection.execute(statement).mappings()]
        return add_categories(connection, records)


def library_choices(engine):
    """Choices come from the whole stored library, independently of filters."""
    choices = dict(categories=[], authors=[], periods=[])
    with engine.connect() as connection:
        if not inspect(connection).has_table(library_text.name):
            return choices
        assigned = select(text_category_assignment.c.text_id).where(
            text_category_assignment.c.category_id == text_category.c.id,
        ).exists()
        statement = select(text_category).where(assigned).order_by(text_category.c.id)
        choices["categories"] = [dict(row) for row in connection.execute(statement).mappings()]
        for column, key in ((library_text.c.author, "authors"), (library_text.c.period, "periods")):
            statement = select(column).distinct().where(column.is_not(None)).order_by(column.collate("BINARY"))
            choices[key] = [value for value in connection.execute(statement).scalars() if value.strip()]
    return choices


def get_text(engine, text_id):
    if not 1 <= text_id <= 2**63 - 1:
        return None
    with engine.connect() as connection:
        if not inspect(connection).has_table(library_text.name):
            return None
        statement = select(*METADATA_COLUMNS, library_text.c.body).where(library_text.c.id == text_id)
        row = connection.execute(statement).mappings().first()
        return add_categories(connection, [dict(row)])[0] if row is not None else None
