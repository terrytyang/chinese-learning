"""The preliminary logical schema, independent of the historical HSK schema."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

metadata = MetaData(
    naming_convention={
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
    }
)

hanzi_character = Table(
    "hanzi_character",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("simplified", String, nullable=False, unique=True),
    Column("traditional", String),
    Column("english_gloss", Text),
    Column("usage_note", Text),
    CheckConstraint("length(simplified) = 1", name="single_simplified"),
    CheckConstraint(
        "traditional IS NULL OR length(traditional) = 1", name="single_traditional"
    ),
)

hsk_scheme = Table(
    "hsk_scheme",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("code", String, nullable=False, unique=True),
    Column("label", Text, nullable=False),
    Column("max_level", Integer, nullable=False),
    CheckConstraint("max_level > 0", name="positive_max_level"),
)

character_hsk_level = Table(
    "character_hsk_level",
    metadata,
    Column("character_id", ForeignKey("hanzi_character.id"), primary_key=True),
    Column("hsk_scheme_id", ForeignKey("hsk_scheme.id"), primary_key=True),
    Column("level", Integer, nullable=False),
    CheckConstraint("level > 0", name="positive_level"),
)

learning_status = Table(
    "learning_status",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("code", String, nullable=False, unique=True),
    Column("label", Text, nullable=False),
)

character_learning = Table(
    "character_learning",
    metadata,
    Column("character_id", ForeignKey("hanzi_character.id"), primary_key=True),
    Column(
        "recognition_status_id", ForeignKey("learning_status.id"), nullable=False
    ),
    Column("production_status_id", ForeignKey("learning_status.id"), nullable=False),
)
