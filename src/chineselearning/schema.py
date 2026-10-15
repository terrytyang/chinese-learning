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
    UniqueConstraint,
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

vocabulary_entry = Table(
    "vocabulary_entry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("simplified", Text, nullable=False),
    CheckConstraint("length(simplified) > 0", name="nonempty_simplified"),
)

vocabulary_reading = Table(
    "vocabulary_reading",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("vocabulary_id", ForeignKey("vocabulary_entry.id"), nullable=False),
    Column("position", Integer, nullable=False),
    Column("traditional", Text, nullable=False),
    Column("pinyin", Text, nullable=False),
    Column("numeric", Text, nullable=False),
    Column("wadegiles", Text, nullable=False),
    Column("bopomofo", Text, nullable=False),
    Column("romatzyh", Text, nullable=False),
    UniqueConstraint("vocabulary_id", "position"),
    CheckConstraint("position > 0", name="positive_position"),
)

vocabulary_meaning = Table(
    "vocabulary_meaning",
    metadata,
    Column("reading_id", ForeignKey("vocabulary_reading.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("meaning", Text, nullable=False),
    CheckConstraint("position > 0", name="positive_position"),
)

vocabulary_hsk_level = Table(
    "vocabulary_hsk_level",
    metadata,
    Column("vocabulary_id", ForeignKey("vocabulary_entry.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("hsk_scheme_id", ForeignKey("hsk_scheme.id"), nullable=False),
    Column("level", Integer, nullable=False),
    CheckConstraint("position > 0", name="positive_position"),
    CheckConstraint("level > 0", name="positive_level"),
)

vocabulary_character = Table(
    "vocabulary_character",
    metadata,
    Column("vocabulary_id", ForeignKey("vocabulary_entry.id"), primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("character_id", ForeignKey("hanzi_character.id"), nullable=False),
    CheckConstraint("position > 0", name="positive_position"),
)

text_category = Table(
    "text_category",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("label", Text, nullable=False),
    CheckConstraint("length(trim(label)) > 0", name="nonblank_label"),
)

library_text = Table(
    "library_text",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("category_id", ForeignKey("text_category.id"), nullable=False),
    Column("author", Text),
    Column("period", Text),
    Column("title", Text, nullable=False),
    Column("body", Text, nullable=False),
    Column("notes", Text),
    CheckConstraint("length(trim(title)) > 0", name="nonblank_title"),
    CheckConstraint("length(trim(body)) > 0", name="nonblank_body"),
)
