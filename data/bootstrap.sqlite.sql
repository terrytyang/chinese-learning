-- Generated from the preliminary SQLAlchemy schema and selected seed data.

-- SQLite snapshot. Import into a fresh database; no source database is needed.

PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE hanzi_character (
	id INTEGER NOT NULL,
	simplified VARCHAR NOT NULL,
	traditional VARCHAR,
	english_gloss TEXT,
	usage_note TEXT,
	CONSTRAINT pk_hanzi_character PRIMARY KEY (id),
	CONSTRAINT ck_hanzi_character_single_simplified CHECK (length(simplified) = 1),
	CONSTRAINT ck_hanzi_character_single_traditional CHECK (traditional IS NULL OR length(traditional) = 1),
	CONSTRAINT uq_hanzi_character_simplified UNIQUE (simplified)
);

CREATE TABLE hsk_scheme (
	id INTEGER NOT NULL,
	code VARCHAR NOT NULL,
	label TEXT NOT NULL,
	max_level INTEGER NOT NULL,
	CONSTRAINT pk_hsk_scheme PRIMARY KEY (id),
	CONSTRAINT ck_hsk_scheme_positive_max_level CHECK (max_level > 0),
	CONSTRAINT uq_hsk_scheme_code UNIQUE (code)
);

CREATE TABLE learning_status (
	id INTEGER NOT NULL,
	code VARCHAR NOT NULL,
	label TEXT NOT NULL,
	CONSTRAINT pk_learning_status PRIMARY KEY (id),
	CONSTRAINT uq_learning_status_code UNIQUE (code)
);

CREATE TABLE library_text (
	id INTEGER NOT NULL,
	author TEXT,
	period TEXT,
	title TEXT NOT NULL,
	body TEXT NOT NULL,
	notes TEXT,
	CONSTRAINT pk_library_text PRIMARY KEY (id),
	CONSTRAINT ck_library_text_nonblank_title CHECK (length(trim(title)) > 0),
	CONSTRAINT ck_library_text_nonblank_body CHECK (length(trim(body)) > 0)
);

CREATE TABLE text_category (
	id INTEGER NOT NULL,
	label TEXT NOT NULL,
	CONSTRAINT pk_text_category PRIMARY KEY (id),
	CONSTRAINT ck_text_category_nonblank_label CHECK (length(trim(label)) > 0)
);

CREATE TABLE vocabulary_entry (
	id INTEGER NOT NULL,
	simplified TEXT NOT NULL,
	CONSTRAINT pk_vocabulary_entry PRIMARY KEY (id),
	CONSTRAINT ck_vocabulary_entry_nonempty_simplified CHECK (length(simplified) > 0)
);

CREATE TABLE character_hsk_level (
	character_id INTEGER NOT NULL,
	hsk_scheme_id INTEGER NOT NULL,
	level INTEGER NOT NULL,
	CONSTRAINT pk_character_hsk_level PRIMARY KEY (character_id, hsk_scheme_id),
	CONSTRAINT ck_character_hsk_level_positive_level CHECK (level > 0),
	CONSTRAINT fk_character_hsk_level_character_id_hanzi_character FOREIGN KEY(character_id) REFERENCES hanzi_character (id),
	CONSTRAINT fk_character_hsk_level_hsk_scheme_id_hsk_scheme FOREIGN KEY(hsk_scheme_id) REFERENCES hsk_scheme (id)
);

CREATE TABLE character_learning (
	character_id INTEGER NOT NULL,
	recognition_status_id INTEGER NOT NULL,
	production_status_id INTEGER NOT NULL,
	CONSTRAINT pk_character_learning PRIMARY KEY (character_id),
	CONSTRAINT fk_character_learning_character_id_hanzi_character FOREIGN KEY(character_id) REFERENCES hanzi_character (id),
	CONSTRAINT fk_character_learning_recognition_status_id_learning_status FOREIGN KEY(recognition_status_id) REFERENCES learning_status (id),
	CONSTRAINT fk_character_learning_production_status_id_learning_status FOREIGN KEY(production_status_id) REFERENCES learning_status (id)
);

CREATE TABLE text_category_assignment (
	text_id INTEGER NOT NULL,
	category_id INTEGER NOT NULL,
	CONSTRAINT pk_text_category_assignment PRIMARY KEY (text_id, category_id),
	CONSTRAINT fk_text_category_assignment_text_id_library_text FOREIGN KEY(text_id) REFERENCES library_text (id),
	CONSTRAINT fk_text_category_assignment_category_id_text_category FOREIGN KEY(category_id) REFERENCES text_category (id)
);

CREATE TABLE vocabulary_character (
	vocabulary_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	character_id INTEGER NOT NULL,
	CONSTRAINT pk_vocabulary_character PRIMARY KEY (vocabulary_id, position),
	CONSTRAINT ck_vocabulary_character_positive_position CHECK (position > 0),
	CONSTRAINT fk_vocabulary_character_vocabulary_id_vocabulary_entry FOREIGN KEY(vocabulary_id) REFERENCES vocabulary_entry (id),
	CONSTRAINT fk_vocabulary_character_character_id_hanzi_character FOREIGN KEY(character_id) REFERENCES hanzi_character (id)
);

CREATE TABLE vocabulary_hsk_level (
	vocabulary_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	hsk_scheme_id INTEGER NOT NULL,
	level INTEGER NOT NULL,
	CONSTRAINT pk_vocabulary_hsk_level PRIMARY KEY (vocabulary_id, position),
	CONSTRAINT ck_vocabulary_hsk_level_positive_position CHECK (position > 0),
	CONSTRAINT ck_vocabulary_hsk_level_positive_level CHECK (level > 0),
	CONSTRAINT fk_vocabulary_hsk_level_vocabulary_id_vocabulary_entry FOREIGN KEY(vocabulary_id) REFERENCES vocabulary_entry (id),
	CONSTRAINT fk_vocabulary_hsk_level_hsk_scheme_id_hsk_scheme FOREIGN KEY(hsk_scheme_id) REFERENCES hsk_scheme (id)
);

CREATE TABLE vocabulary_reading (
	id INTEGER NOT NULL,
	vocabulary_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	traditional TEXT NOT NULL,
	pinyin TEXT NOT NULL,
	numeric TEXT NOT NULL,
	wadegiles TEXT NOT NULL,
	bopomofo TEXT NOT NULL,
	romatzyh TEXT NOT NULL,
	CONSTRAINT pk_vocabulary_reading PRIMARY KEY (id),
	CONSTRAINT uq_vocabulary_reading_vocabulary_id UNIQUE (vocabulary_id, position),
	CONSTRAINT ck_vocabulary_reading_positive_position CHECK (position > 0),
	CONSTRAINT fk_vocabulary_reading_vocabulary_id_vocabulary_entry FOREIGN KEY(vocabulary_id) REFERENCES vocabulary_entry (id)
);

CREATE TABLE vocabulary_meaning (
	reading_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	meaning TEXT NOT NULL,
	CONSTRAINT pk_vocabulary_meaning PRIMARY KEY (reading_id, position),
	CONSTRAINT ck_vocabulary_meaning_positive_position CHECK (position > 0),
	CONSTRAINT fk_vocabulary_meaning_reading_id_vocabulary_reading FOREIGN KEY(reading_id) REFERENCES vocabulary_reading (id)
);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (1, '学', '學', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (2, '银', '銀', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (3, '行', '行', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (4, '客', '客', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (5, '发', '發', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (6, '后', '后', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (7, '么', '麼', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (8, '服', '服', NULL, NULL);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (1, 'new', 'HSK 3.0 (2021 standard)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (2, 'newest', 'HSK 3.0 (2026 syllabus)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (3, 'old', 'HSK 2.0', 6);

INSERT INTO learning_status (id, code, label) VALUES (1, 'not_encountered', 'Not yet encountered');

INSERT INTO learning_status (id, code, label) VALUES (2, 'learning', 'Learning');

INSERT INTO learning_status (id, code, label) VALUES (3, 'known', 'Known');

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 3, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (1, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (2, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (3, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (4, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (5, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (6, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (7, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (8, 1, 1);

COMMIT;
