"""Read-only application inventory queries, independent of HTTP and rendering."""

from pathlib import Path
import sqlite3

from sqlalchemy import create_engine, func, inspect, select

from chineselearning.schema import (
    character_hsk_level, character_learning, hanzi_character, hsk_scheme,
    learning_status,
    library_text, text_category, text_category_assignment,
)

SCHEMES = ("old", "new", "newest")
PAGE_SIZES = (10, 20, 50, 100)
# Only these SQLAlchemy expressions can be used for ordering.
SORT_FIELDS = {
    "simplified": hanzi_character.c.simplified.collate("BINARY"),
    "hsk_level": character_hsk_level.c.level,
}


class InvalidInventoryQuery(ValueError):
    pass


def level_label(scheme, level):
    return "7–9" if scheme in ("new", "newest") and level == 7 else str(level)


def open_inventory_database(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"Application database does not exist: {path}. Build it explicitly first.")
    uri = path.as_uri() + "?mode=ro"

    def connect():
        connection = sqlite3.connect(uri, uri=True, check_same_thread=False)
        connection.execute("PRAGMA query_only = ON")
        return connection

    engine = create_engine("sqlite+pysqlite://", creator=connect)
    try:
        inspector = inspect(engine)
        tables = [hanzi_character, hsk_scheme, character_hsk_level,
                  learning_status, character_learning]
        if inspector.has_table(library_text.name):
            tables.extend([library_text, text_category, text_category_assignment])
        for table in tables:
            if not inspector.has_table(table.name):
                raise ValueError("Database is not an initialized application inventory; rebuild it")
            columns = {column["name"] for column in inspector.get_columns(table.name)}
            if not set(table.c.keys()) <= columns:
                raise ValueError(f"Application database has incompatible columns: {table.name}")
    except BaseException:
        engine.dispose()
        raise
    return engine


def list_characters(engine, *, hsk_scheme_code="newest", hsk_level=None,
                    page=1, page_size=20, sort="simplified", order="asc"):
    if hsk_scheme_code not in SCHEMES:
        raise InvalidInventoryQuery("Unknown HSK scheme")
    if type(page) is not int or page < 1:
        raise InvalidInventoryQuery("Page must be a positive integer")
    if type(page_size) is not int or page_size not in PAGE_SIZES:
        raise InvalidInventoryQuery("Page size must be 10, 20, 50, or 100")
    if sort not in SORT_FIELDS or order not in ("asc", "desc"):
        raise InvalidInventoryQuery("Invalid sort field or direction")
    recognition = learning_status.alias("recognition")
    production = learning_status.alias("production")
    joined = (hanzi_character.join(character_hsk_level)
              .outerjoin(character_learning)
              .outerjoin(recognition, recognition.c.id == character_learning.c.recognition_status_id)
              .outerjoin(production, production.c.id == character_learning.c.production_status_id))
    with engine.connect() as connection:
        scheme = connection.execute(select(hsk_scheme).where(
            hsk_scheme.c.code == hsk_scheme_code
        )).mappings().first()
        if scheme is None:
            raise InvalidInventoryQuery("HSK scheme is unavailable in this database")
        if hsk_level is not None and (
            type(hsk_level) is not int or not 1 <= hsk_level <= scheme["max_level"]
        ):
            raise InvalidInventoryQuery(f"Band must be between 1 and {scheme['max_level']} for this scheme")
        conditions = [character_hsk_level.c.hsk_scheme_id == scheme["id"]]
        if hsk_level is not None:
            conditions.append(character_hsk_level.c.level == hsk_level)
        total = connection.execute(select(func.count()).select_from(joined).where(*conditions)).scalar_one()
        total_pages = (total + page_size - 1) // page_size
        items = []
        if page <= total_pages:
            columns = [SORT_FIELDS[sort]]
            if sort == "hsk_level":
                columns.append(SORT_FIELDS["simplified"])
            columns.append(hanzi_character.c.id)
            ordering = [column.asc() if order == "asc" else column.desc() for column in columns]
            statement = (select(
                hanzi_character, character_hsk_level.c.level.label("hsk_level"),
                recognition.c.code.label("recognition_status"),
                production.c.code.label("production_status"),
            ).select_from(joined).where(*conditions).order_by(*ordering)
                .limit(page_size).offset((page - 1) * page_size))
            for row in connection.execute(statement).mappings():
                item = dict(row)
                item["hsk_level_label"] = level_label(hsk_scheme_code, item["hsk_level"])
                items.append(item)
    return {
        "items": items, "total": total, "page": page, "page_size": page_size,
        "total_pages": total_pages,
        "hsk_scheme": {"code": scheme["code"], "label": scheme["label"]},
    }
