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

CREATE TABLE library_text (
	id INTEGER NOT NULL,
	category_id INTEGER NOT NULL,
	author TEXT,
	period TEXT,
	title TEXT NOT NULL,
	body TEXT NOT NULL,
	notes TEXT,
	CONSTRAINT pk_library_text PRIMARY KEY (id),
	CONSTRAINT ck_library_text_nonblank_title CHECK (length(trim(title)) > 0),
	CONSTRAINT ck_library_text_nonblank_body CHECK (length(trim(body)) > 0),
	CONSTRAINT fk_library_text_category_id_text_category FOREIGN KEY(category_id) REFERENCES text_category (id)
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

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (1, '一', '一', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (2, '七', '七', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (3, '三', '三', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (4, '上', '上', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (5, '下', '下', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (6, '不', '不', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (7, '东', '東', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (8, '两', '兩', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (9, '个', '個', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (10, '中', '中', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (11, '么', '麼', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (12, '九', '九', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (13, '也', '也', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (14, '习', '習', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (15, '书', '書', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (16, '买', '買', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (17, '了', '了', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (18, '事', '事', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (19, '二', '二', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (20, '五', '五', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (21, '些', '些', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (22, '亮', '亮', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (23, '人', '人', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (24, '什', '什', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (25, '今', '今', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (26, '他', '他', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (27, '以', '㕥', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (28, '们', '們', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (29, '件', '件', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (30, '休', '休', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (31, '会', '會', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (32, '住', '住', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (33, '作', '作', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (34, '你', '你', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (35, '便', '便', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (36, '候', '候', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (37, '做', '做', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (38, '儿', '兒', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (39, '元', '元', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (40, '先', '先', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (41, '八', '八', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (42, '公', '公', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (43, '六', '六', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (44, '关', '關', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (45, '兴', '興', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (46, '再', '再', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (47, '写', '寫', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (48, '冷', '冷', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (49, '几', '几', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (50, '出', '出', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (51, '分', '分', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (52, '到', '到', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (53, '前', '前', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (54, '包', '包', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (55, '医', '醫', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (56, '十', '十', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (57, '千', '千', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (58, '午', '午', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (59, '半', '半', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (60, '卖', '賣', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (61, '去', '去', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (62, '友', '友', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (63, '口', '口', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (64, '只', '只', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (65, '叫', '叫', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (66, '可', '可', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (67, '号', '號', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (68, '司', '司', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (69, '吃', '吃', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (70, '同', '同', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (71, '名', '名', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (72, '后', '后', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (73, '吗', '嗎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (74, '吧', '吧', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (75, '听', '听', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (76, '呢', '呢', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (77, '和', '咊', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (78, '哥', '哥', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (79, '哪', '哪', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (80, '唱', '唱', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (81, '商', '商', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (82, '喂', '喂', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (83, '喜', '喜', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (84, '喝', '喝', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (85, '四', '四', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (86, '回', '回', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (87, '国', '國', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (88, '在', '在', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (89, '坐', '坐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (90, '块', '塊', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (91, '士', '士', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (92, '外', '外', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (93, '多', '多', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (94, '大', '大', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (95, '天', '天', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (96, '太', '太', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (97, '女', '女', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (98, '奶', '奶', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (99, '她', '她', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (100, '好', '好', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (101, '妈', '媽', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (102, '妹', '妹', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (103, '姐', '姐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (104, '子', '子', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (105, '字', '字', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (106, '学', '學', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (107, '孩', '孩', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (108, '它', '它', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (109, '宜', '宜', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (110, '客', '客', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (111, '家', '傢', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (112, '对', '對', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (113, '小', '小', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (114, '少', '少', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (115, '岁', '嵗', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (116, '工', '工', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (117, '市', '市', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (118, '师', '師', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (119, '常', '常', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (120, '年', '年', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (121, '床', '床', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (122, '店', '店', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (123, '开', '開', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (124, '弟', '弟', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (125, '影', '影', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (126, '很', '很', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (127, '得', '得', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (128, '忙', '忙', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (129, '怎', '怎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (130, '息', '息', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (131, '您', '您', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (132, '想', '想', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (133, '我', '我', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (134, '房', '房', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (135, '手', '手', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (136, '打', '打', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (137, '找', '找', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (138, '文', '文', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (139, '新', '新', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (140, '日', '日', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (141, '早', '早', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (142, '时', '旹', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (143, '明', '明', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (144, '星', '星', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (145, '昨', '昨', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (146, '是', '是', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (147, '晚', '晚', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (148, '月', '月', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (149, '有', '有', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (150, '朋', '朋', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (151, '服', '服', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (152, '期', '朞', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (153, '本', '本', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (154, '机', '機', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (155, '条', '條', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (156, '来', '來', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (157, '杯', '杯', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (158, '果', '果', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (159, '校', '校', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (160, '样', '樣', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (161, '桌', '桌', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (162, '椅', '椅', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (163, '欢', '歡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (164, '歌', '歌', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (165, '正', '正', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (166, '气', '氣', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (167, '水', '水', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (168, '汉', '漢', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (169, '没', '沒', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (170, '漂', '漂', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (171, '火', '火', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (172, '点', '點', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (173, '热', '熱', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (174, '爱', '愛', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (175, '爸', '爸', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (176, '牛', '牛', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (177, '狗', '狗', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (178, '猫', '貓', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (179, '玩', '玩', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (180, '现', '現', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (181, '班', '班', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (182, '生', '生', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (183, '电', '電', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (184, '男', '男', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (185, '病', '病', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (186, '白', '白', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (187, '百', '百', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (188, '的', '的', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (189, '看', '看', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (190, '真', '真', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (191, '睡', '睡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (192, '知', '知', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (193, '租', '租', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (194, '穿', '穿', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (195, '第', '第', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (196, '米', '米', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (197, '系', '係', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (198, '给', '給', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (199, '老', '老', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (200, '能', '能', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (201, '脑', '腦', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (202, '苹', '蘋', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (203, '茶', '茶', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (204, '菜', '菜', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (205, '蛋', '蛋', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (206, '衣', '衣', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (207, '西', '西', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (208, '要', '要', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (209, '见', '見', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (210, '视', '視', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (211, '觉', '覺', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (212, '认', '認', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (213, '识', '識', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (214, '话', '話', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (215, '语', '語', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (216, '说', '說', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (217, '请', '請', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (218, '读', '讀', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (219, '课', '課', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (220, '谁', '誰', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (221, '谢', '謝', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (222, '贵', '貴', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (223, '起', '起', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (224, '超', '超', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (225, '车', '車', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (226, '边', '邊', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (227, '还', '還', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (228, '这', '這', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (229, '道', '道', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (230, '那', '那', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (231, '都', '都', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (232, '里', '裏', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (233, '钟', '鍾', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (234, '钱', '錢', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (235, '问', '問', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (236, '间', '間', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (237, '院', '院', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (238, '雨', '雨', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (239, '雪', '雪', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (240, '零', '零', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (241, '非', '非', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (242, '面', '面', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (243, '题', '題', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (244, '飞', '飛', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (245, '饭', '飯', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (246, '饺', '餃', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (247, '高', '高', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (248, '鸡', '雞', NULL, NULL);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (1, 'new', 'HSK 3.0 (2021 standard)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (2, 'newest', 'HSK 3.0 (2026 syllabus)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (3, 'old', 'HSK 2.0', 6);

INSERT INTO learning_status (id, code, label) VALUES (1, 'not_encountered', 'Not yet encountered');

INSERT INTO learning_status (id, code, label) VALUES (2, 'learning', 'Learning');

INSERT INTO learning_status (id, code, label) VALUES (3, 'known', 'Known');

INSERT INTO text_category (id, label) VALUES (1, '诗词');

INSERT INTO text_category (id, label) VALUES (2, '文言');

INSERT INTO text_category (id, label) VALUES (3, '散文');

INSERT INTO text_category (id, label) VALUES (4, '节选');

INSERT INTO text_category (id, label) VALUES (5, '讲解');

INSERT INTO vocabulary_entry (id, simplified) VALUES (1, '爱');

INSERT INTO vocabulary_entry (id, simplified) VALUES (2, '八');

INSERT INTO vocabulary_entry (id, simplified) VALUES (3, '爸爸');

INSERT INTO vocabulary_entry (id, simplified) VALUES (4, '吧');

INSERT INTO vocabulary_entry (id, simplified) VALUES (5, '白天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (6, '百');

INSERT INTO vocabulary_entry (id, simplified) VALUES (7, '半');

INSERT INTO vocabulary_entry (id, simplified) VALUES (8, '包子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (9, '杯子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (10, '本');

INSERT INTO vocabulary_entry (id, simplified) VALUES (11, '边');

INSERT INTO vocabulary_entry (id, simplified) VALUES (12, '便宜');

INSERT INTO vocabulary_entry (id, simplified) VALUES (13, '病');

INSERT INTO vocabulary_entry (id, simplified) VALUES (14, '不');

INSERT INTO vocabulary_entry (id, simplified) VALUES (15, '不客气');

INSERT INTO vocabulary_entry (id, simplified) VALUES (16, '不要');

INSERT INTO vocabulary_entry (id, simplified) VALUES (17, '菜');

INSERT INTO vocabulary_entry (id, simplified) VALUES (18, '茶');

INSERT INTO vocabulary_entry (id, simplified) VALUES (19, '唱');

INSERT INTO vocabulary_entry (id, simplified) VALUES (20, '超市');

INSERT INTO vocabulary_entry (id, simplified) VALUES (21, '车');

INSERT INTO vocabulary_entry (id, simplified) VALUES (22, '吃');

INSERT INTO vocabulary_entry (id, simplified) VALUES (23, '出租车');

INSERT INTO vocabulary_entry (id, simplified) VALUES (24, '穿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (25, '打电话');

INSERT INTO vocabulary_entry (id, simplified) VALUES (26, '大');

INSERT INTO vocabulary_entry (id, simplified) VALUES (27, '大家');

INSERT INTO vocabulary_entry (id, simplified) VALUES (28, '大学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (29, '大学生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (30, '到');

INSERT INTO vocabulary_entry (id, simplified) VALUES (31, '的');

INSERT INTO vocabulary_entry (id, simplified) VALUES (32, '弟弟');

INSERT INTO vocabulary_entry (id, simplified) VALUES (33, '第');

INSERT INTO vocabulary_entry (id, simplified) VALUES (34, '点');

INSERT INTO vocabulary_entry (id, simplified) VALUES (35, '电话');

INSERT INTO vocabulary_entry (id, simplified) VALUES (36, '电脑');

INSERT INTO vocabulary_entry (id, simplified) VALUES (37, '电视');

INSERT INTO vocabulary_entry (id, simplified) VALUES (38, '电影');

INSERT INTO vocabulary_entry (id, simplified) VALUES (39, '电影院');

INSERT INTO vocabulary_entry (id, simplified) VALUES (40, '店');

INSERT INTO vocabulary_entry (id, simplified) VALUES (41, '东西');

INSERT INTO vocabulary_entry (id, simplified) VALUES (42, '都');

INSERT INTO vocabulary_entry (id, simplified) VALUES (43, '读');

INSERT INTO vocabulary_entry (id, simplified) VALUES (44, '读书');

INSERT INTO vocabulary_entry (id, simplified) VALUES (45, '对');

INSERT INTO vocabulary_entry (id, simplified) VALUES (46, '对不起');

INSERT INTO vocabulary_entry (id, simplified) VALUES (47, '多');

INSERT INTO vocabulary_entry (id, simplified) VALUES (48, '多少');

INSERT INTO vocabulary_entry (id, simplified) VALUES (49, '儿子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (50, '二');

INSERT INTO vocabulary_entry (id, simplified) VALUES (51, '饭');

INSERT INTO vocabulary_entry (id, simplified) VALUES (52, '饭店');

INSERT INTO vocabulary_entry (id, simplified) VALUES (53, '房间');

INSERT INTO vocabulary_entry (id, simplified) VALUES (54, '飞机');

INSERT INTO vocabulary_entry (id, simplified) VALUES (55, '非常');

INSERT INTO vocabulary_entry (id, simplified) VALUES (56, '分');

INSERT INTO vocabulary_entry (id, simplified) VALUES (57, '分钟');

INSERT INTO vocabulary_entry (id, simplified) VALUES (58, '高兴');

INSERT INTO vocabulary_entry (id, simplified) VALUES (59, '哥哥');

INSERT INTO vocabulary_entry (id, simplified) VALUES (60, '歌');

INSERT INTO vocabulary_entry (id, simplified) VALUES (61, '个');

INSERT INTO vocabulary_entry (id, simplified) VALUES (62, '给');

INSERT INTO vocabulary_entry (id, simplified) VALUES (63, '工作');

INSERT INTO vocabulary_entry (id, simplified) VALUES (64, '公司');

INSERT INTO vocabulary_entry (id, simplified) VALUES (65, '狗');

INSERT INTO vocabulary_entry (id, simplified) VALUES (66, '贵');

INSERT INTO vocabulary_entry (id, simplified) VALUES (67, '国');

INSERT INTO vocabulary_entry (id, simplified) VALUES (68, '还');

INSERT INTO vocabulary_entry (id, simplified) VALUES (69, '孩子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (70, '汉语');

INSERT INTO vocabulary_entry (id, simplified) VALUES (71, '汉字');

INSERT INTO vocabulary_entry (id, simplified) VALUES (72, '好');

INSERT INTO vocabulary_entry (id, simplified) VALUES (73, '好吃');

INSERT INTO vocabulary_entry (id, simplified) VALUES (74, '好看');

INSERT INTO vocabulary_entry (id, simplified) VALUES (75, '好听');

INSERT INTO vocabulary_entry (id, simplified) VALUES (76, '好玩儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (77, '号');

INSERT INTO vocabulary_entry (id, simplified) VALUES (78, '喝');

INSERT INTO vocabulary_entry (id, simplified) VALUES (79, '和');

INSERT INTO vocabulary_entry (id, simplified) VALUES (80, '很');

INSERT INTO vocabulary_entry (id, simplified) VALUES (81, '后');

INSERT INTO vocabulary_entry (id, simplified) VALUES (82, '回');

INSERT INTO vocabulary_entry (id, simplified) VALUES (83, '会');

INSERT INTO vocabulary_entry (id, simplified) VALUES (84, '火车');

INSERT INTO vocabulary_entry (id, simplified) VALUES (85, '鸡蛋');

INSERT INTO vocabulary_entry (id, simplified) VALUES (86, '几');

INSERT INTO vocabulary_entry (id, simplified) VALUES (87, '家');

INSERT INTO vocabulary_entry (id, simplified) VALUES (88, '家人');

INSERT INTO vocabulary_entry (id, simplified) VALUES (89, '见');

INSERT INTO vocabulary_entry (id, simplified) VALUES (90, '件');

INSERT INTO vocabulary_entry (id, simplified) VALUES (91, '饺子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (92, '叫');

INSERT INTO vocabulary_entry (id, simplified) VALUES (93, '姐姐');

INSERT INTO vocabulary_entry (id, simplified) VALUES (94, '今年');

INSERT INTO vocabulary_entry (id, simplified) VALUES (95, '今天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (96, '九');

INSERT INTO vocabulary_entry (id, simplified) VALUES (97, '觉得');

INSERT INTO vocabulary_entry (id, simplified) VALUES (98, '开');

INSERT INTO vocabulary_entry (id, simplified) VALUES (99, '开车');

INSERT INTO vocabulary_entry (id, simplified) VALUES (100, '看');

INSERT INTO vocabulary_entry (id, simplified) VALUES (101, '看病');

INSERT INTO vocabulary_entry (id, simplified) VALUES (102, '看见');

INSERT INTO vocabulary_entry (id, simplified) VALUES (103, '可以');

INSERT INTO vocabulary_entry (id, simplified) VALUES (104, '课');

INSERT INTO vocabulary_entry (id, simplified) VALUES (105, '口');

INSERT INTO vocabulary_entry (id, simplified) VALUES (106, '块');

INSERT INTO vocabulary_entry (id, simplified) VALUES (107, '来');

INSERT INTO vocabulary_entry (id, simplified) VALUES (108, '老师');

INSERT INTO vocabulary_entry (id, simplified) VALUES (109, '了');

INSERT INTO vocabulary_entry (id, simplified) VALUES (110, '冷');

INSERT INTO vocabulary_entry (id, simplified) VALUES (111, '里');

INSERT INTO vocabulary_entry (id, simplified) VALUES (112, '两');

INSERT INTO vocabulary_entry (id, simplified) VALUES (113, '零');

INSERT INTO vocabulary_entry (id, simplified) VALUES (114, '六');

INSERT INTO vocabulary_entry (id, simplified) VALUES (115, '妈妈');

INSERT INTO vocabulary_entry (id, simplified) VALUES (116, '吗');

INSERT INTO vocabulary_entry (id, simplified) VALUES (117, '买');

INSERT INTO vocabulary_entry (id, simplified) VALUES (118, '卖');

INSERT INTO vocabulary_entry (id, simplified) VALUES (119, '忙');

INSERT INTO vocabulary_entry (id, simplified) VALUES (120, '猫');

INSERT INTO vocabulary_entry (id, simplified) VALUES (121, '没关系');

INSERT INTO vocabulary_entry (id, simplified) VALUES (122, '没有');

INSERT INTO vocabulary_entry (id, simplified) VALUES (123, '妹妹');

INSERT INTO vocabulary_entry (id, simplified) VALUES (124, '们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (125, '米饭');

INSERT INTO vocabulary_entry (id, simplified) VALUES (126, '面包');

INSERT INTO vocabulary_entry (id, simplified) VALUES (127, '面条儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (128, '名字');

INSERT INTO vocabulary_entry (id, simplified) VALUES (129, '明年');

INSERT INTO vocabulary_entry (id, simplified) VALUES (130, '明天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (131, '哪');

INSERT INTO vocabulary_entry (id, simplified) VALUES (132, '哪儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (133, '哪里');

INSERT INTO vocabulary_entry (id, simplified) VALUES (134, '哪些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (135, '那');

INSERT INTO vocabulary_entry (id, simplified) VALUES (136, '那边');

INSERT INTO vocabulary_entry (id, simplified) VALUES (137, '那儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (138, '那里');

INSERT INTO vocabulary_entry (id, simplified) VALUES (139, '那些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (140, '男');

INSERT INTO vocabulary_entry (id, simplified) VALUES (141, '男朋友');

INSERT INTO vocabulary_entry (id, simplified) VALUES (142, '呢');

INSERT INTO vocabulary_entry (id, simplified) VALUES (143, '能');

INSERT INTO vocabulary_entry (id, simplified) VALUES (144, '你');

INSERT INTO vocabulary_entry (id, simplified) VALUES (145, '你们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (146, '年');

INSERT INTO vocabulary_entry (id, simplified) VALUES (147, '您');

INSERT INTO vocabulary_entry (id, simplified) VALUES (148, '牛奶');

INSERT INTO vocabulary_entry (id, simplified) VALUES (149, '女');

INSERT INTO vocabulary_entry (id, simplified) VALUES (150, '女儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (151, '女朋友');

INSERT INTO vocabulary_entry (id, simplified) VALUES (152, '女士');

INSERT INTO vocabulary_entry (id, simplified) VALUES (153, '朋友');

INSERT INTO vocabulary_entry (id, simplified) VALUES (154, '漂亮');

INSERT INTO vocabulary_entry (id, simplified) VALUES (155, '苹果');

INSERT INTO vocabulary_entry (id, simplified) VALUES (156, '七');

INSERT INTO vocabulary_entry (id, simplified) VALUES (157, '起床');

INSERT INTO vocabulary_entry (id, simplified) VALUES (158, '千');

INSERT INTO vocabulary_entry (id, simplified) VALUES (159, '前');

INSERT INTO vocabulary_entry (id, simplified) VALUES (160, '钱');

INSERT INTO vocabulary_entry (id, simplified) VALUES (161, '请');

INSERT INTO vocabulary_entry (id, simplified) VALUES (162, '请问');

INSERT INTO vocabulary_entry (id, simplified) VALUES (163, '去');

INSERT INTO vocabulary_entry (id, simplified) VALUES (164, '去年');

INSERT INTO vocabulary_entry (id, simplified) VALUES (165, '热');

INSERT INTO vocabulary_entry (id, simplified) VALUES (166, '人');

INSERT INTO vocabulary_entry (id, simplified) VALUES (167, '认识');

INSERT INTO vocabulary_entry (id, simplified) VALUES (168, '日');

INSERT INTO vocabulary_entry (id, simplified) VALUES (169, '三');

INSERT INTO vocabulary_entry (id, simplified) VALUES (170, '商店');

INSERT INTO vocabulary_entry (id, simplified) VALUES (171, '上');

INSERT INTO vocabulary_entry (id, simplified) VALUES (172, '上班');

INSERT INTO vocabulary_entry (id, simplified) VALUES (173, '上课');

INSERT INTO vocabulary_entry (id, simplified) VALUES (174, '上午');

INSERT INTO vocabulary_entry (id, simplified) VALUES (175, '上学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (176, '少');

INSERT INTO vocabulary_entry (id, simplified) VALUES (177, '什么');

INSERT INTO vocabulary_entry (id, simplified) VALUES (178, '生病');

INSERT INTO vocabulary_entry (id, simplified) VALUES (179, '十');

INSERT INTO vocabulary_entry (id, simplified) VALUES (180, '时候');

INSERT INTO vocabulary_entry (id, simplified) VALUES (181, '时间');

INSERT INTO vocabulary_entry (id, simplified) VALUES (182, '事');

INSERT INTO vocabulary_entry (id, simplified) VALUES (183, '是');

INSERT INTO vocabulary_entry (id, simplified) VALUES (184, '手机');

INSERT INTO vocabulary_entry (id, simplified) VALUES (185, '书');

INSERT INTO vocabulary_entry (id, simplified) VALUES (186, '书店');

INSERT INTO vocabulary_entry (id, simplified) VALUES (187, '谁');

INSERT INTO vocabulary_entry (id, simplified) VALUES (188, '水');

INSERT INTO vocabulary_entry (id, simplified) VALUES (189, '水果');

INSERT INTO vocabulary_entry (id, simplified) VALUES (190, '睡');

INSERT INTO vocabulary_entry (id, simplified) VALUES (191, '睡觉');

INSERT INTO vocabulary_entry (id, simplified) VALUES (192, '说');

INSERT INTO vocabulary_entry (id, simplified) VALUES (193, '说话');

INSERT INTO vocabulary_entry (id, simplified) VALUES (194, '四');

INSERT INTO vocabulary_entry (id, simplified) VALUES (195, '岁');

INSERT INTO vocabulary_entry (id, simplified) VALUES (196, '他');

INSERT INTO vocabulary_entry (id, simplified) VALUES (197, '他们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (198, '它');

INSERT INTO vocabulary_entry (id, simplified) VALUES (199, '它们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (200, '她');

INSERT INTO vocabulary_entry (id, simplified) VALUES (201, '她们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (202, '太');

INSERT INTO vocabulary_entry (id, simplified) VALUES (203, '天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (204, '天气');

INSERT INTO vocabulary_entry (id, simplified) VALUES (205, '听');

INSERT INTO vocabulary_entry (id, simplified) VALUES (206, '听见');

INSERT INTO vocabulary_entry (id, simplified) VALUES (207, '同学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (208, '外');

INSERT INTO vocabulary_entry (id, simplified) VALUES (209, '外边');

INSERT INTO vocabulary_entry (id, simplified) VALUES (210, '玩');

INSERT INTO vocabulary_entry (id, simplified) VALUES (211, '晚');

INSERT INTO vocabulary_entry (id, simplified) VALUES (212, '晚饭');

INSERT INTO vocabulary_entry (id, simplified) VALUES (213, '晚上');

INSERT INTO vocabulary_entry (id, simplified) VALUES (214, '喂');

INSERT INTO vocabulary_entry (id, simplified) VALUES (215, '问');

INSERT INTO vocabulary_entry (id, simplified) VALUES (216, '问题');

INSERT INTO vocabulary_entry (id, simplified) VALUES (217, '我');

INSERT INTO vocabulary_entry (id, simplified) VALUES (218, '我们');

INSERT INTO vocabulary_entry (id, simplified) VALUES (219, '五');

INSERT INTO vocabulary_entry (id, simplified) VALUES (220, '午饭');

INSERT INTO vocabulary_entry (id, simplified) VALUES (221, '喜欢');

INSERT INTO vocabulary_entry (id, simplified) VALUES (222, '下');

INSERT INTO vocabulary_entry (id, simplified) VALUES (223, '下班');

INSERT INTO vocabulary_entry (id, simplified) VALUES (224, '下课');

INSERT INTO vocabulary_entry (id, simplified) VALUES (225, '下午');

INSERT INTO vocabulary_entry (id, simplified) VALUES (226, '下雨');

INSERT INTO vocabulary_entry (id, simplified) VALUES (227, '先生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (228, '现在');

INSERT INTO vocabulary_entry (id, simplified) VALUES (229, '想');

INSERT INTO vocabulary_entry (id, simplified) VALUES (230, '小');

INSERT INTO vocabulary_entry (id, simplified) VALUES (231, '小朋友');

INSERT INTO vocabulary_entry (id, simplified) VALUES (232, '小时');

INSERT INTO vocabulary_entry (id, simplified) VALUES (233, '小学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (234, '小学生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (235, '些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (236, '写');

INSERT INTO vocabulary_entry (id, simplified) VALUES (237, '谢谢');

INSERT INTO vocabulary_entry (id, simplified) VALUES (238, '新');

INSERT INTO vocabulary_entry (id, simplified) VALUES (239, '星期');

INSERT INTO vocabulary_entry (id, simplified) VALUES (240, '星期日');

INSERT INTO vocabulary_entry (id, simplified) VALUES (241, '星期天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (242, '休息');

INSERT INTO vocabulary_entry (id, simplified) VALUES (243, '学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (244, '学生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (245, '学习');

INSERT INTO vocabulary_entry (id, simplified) VALUES (246, '学校');

INSERT INTO vocabulary_entry (id, simplified) VALUES (247, '雪');

INSERT INTO vocabulary_entry (id, simplified) VALUES (248, '要');

INSERT INTO vocabulary_entry (id, simplified) VALUES (249, '也');

INSERT INTO vocabulary_entry (id, simplified) VALUES (250, '一');

INSERT INTO vocabulary_entry (id, simplified) VALUES (251, '一半');

INSERT INTO vocabulary_entry (id, simplified) VALUES (252, '一点儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (253, '一些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (254, '衣服');

INSERT INTO vocabulary_entry (id, simplified) VALUES (255, '医生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (256, '医院');

INSERT INTO vocabulary_entry (id, simplified) VALUES (257, '椅子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (258, '有');

INSERT INTO vocabulary_entry (id, simplified) VALUES (259, '有的');

INSERT INTO vocabulary_entry (id, simplified) VALUES (260, '有点儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (261, '有些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (262, '雨');

INSERT INTO vocabulary_entry (id, simplified) VALUES (263, '元');

INSERT INTO vocabulary_entry (id, simplified) VALUES (264, '月');

INSERT INTO vocabulary_entry (id, simplified) VALUES (265, '再');

INSERT INTO vocabulary_entry (id, simplified) VALUES (266, '再见');

INSERT INTO vocabulary_entry (id, simplified) VALUES (267, '在');

INSERT INTO vocabulary_entry (id, simplified) VALUES (268, '早');

INSERT INTO vocabulary_entry (id, simplified) VALUES (269, '早饭');

INSERT INTO vocabulary_entry (id, simplified) VALUES (270, '早上');

INSERT INTO vocabulary_entry (id, simplified) VALUES (271, '怎么');

INSERT INTO vocabulary_entry (id, simplified) VALUES (272, '怎么样');

INSERT INTO vocabulary_entry (id, simplified) VALUES (273, '找');

INSERT INTO vocabulary_entry (id, simplified) VALUES (274, '这');

INSERT INTO vocabulary_entry (id, simplified) VALUES (275, '这边');

INSERT INTO vocabulary_entry (id, simplified) VALUES (276, '这儿');

INSERT INTO vocabulary_entry (id, simplified) VALUES (277, '这里');

INSERT INTO vocabulary_entry (id, simplified) VALUES (278, '这些');

INSERT INTO vocabulary_entry (id, simplified) VALUES (279, '真');

INSERT INTO vocabulary_entry (id, simplified) VALUES (280, '正在');

INSERT INTO vocabulary_entry (id, simplified) VALUES (281, '知道');

INSERT INTO vocabulary_entry (id, simplified) VALUES (282, '只');

INSERT INTO vocabulary_entry (id, simplified) VALUES (283, '中国');

INSERT INTO vocabulary_entry (id, simplified) VALUES (284, '中文');

INSERT INTO vocabulary_entry (id, simplified) VALUES (285, '中午');

INSERT INTO vocabulary_entry (id, simplified) VALUES (286, '中学');

INSERT INTO vocabulary_entry (id, simplified) VALUES (287, '中学生');

INSERT INTO vocabulary_entry (id, simplified) VALUES (288, '住');

INSERT INTO vocabulary_entry (id, simplified) VALUES (289, '桌子');

INSERT INTO vocabulary_entry (id, simplified) VALUES (290, '字');

INSERT INTO vocabulary_entry (id, simplified) VALUES (291, '昨天');

INSERT INTO vocabulary_entry (id, simplified) VALUES (292, '坐');

INSERT INTO vocabulary_entry (id, simplified) VALUES (293, '做');

INSERT INTO vocabulary_entry (id, simplified) VALUES (294, '做饭');

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (2, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (3, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (4, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (5, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (7, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (8, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (9, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (9, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (9, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (10, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (10, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (10, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (132, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (132, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (132, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (133, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (133, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (133, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (134, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (134, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (134, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (135, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (135, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (135, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (137, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (137, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (137, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (138, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (138, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (138, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (139, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (139, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (139, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (140, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (140, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (140, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (141, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (141, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (141, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (142, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (142, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (142, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (143, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (143, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (143, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (144, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (144, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (144, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (145, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (145, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (145, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (146, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (146, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (146, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (147, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (147, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (147, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (148, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (148, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (148, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (149, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (149, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (149, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (150, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (150, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (150, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (151, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (151, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (151, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (152, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (152, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (152, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (153, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (153, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (153, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (154, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (154, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (154, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (155, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (155, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (155, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (156, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (156, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (156, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (157, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (157, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (157, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (158, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (158, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (158, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (159, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (159, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (159, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (160, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (160, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (160, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (161, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (161, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (161, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (162, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (162, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (162, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (163, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (163, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (163, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (164, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (164, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (164, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (165, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (165, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (165, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (166, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (166, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (166, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (167, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (167, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (167, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (168, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (168, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (168, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (169, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (169, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (169, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (170, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (170, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (170, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (171, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (171, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (171, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (172, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (172, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (172, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (173, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (173, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (173, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (174, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (174, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (174, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (175, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (175, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (175, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (176, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (176, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (176, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (177, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (177, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (177, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (178, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (178, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (178, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (179, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (179, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (179, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (180, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (180, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (180, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (181, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (181, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (181, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (182, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (182, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (182, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (183, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (183, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (183, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (184, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (184, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (184, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (185, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (185, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (185, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (186, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (186, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (186, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (187, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (187, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (187, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (188, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (188, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (188, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (189, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (189, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (189, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (190, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (190, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (190, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (191, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (191, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (191, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (192, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (192, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (192, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (193, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (193, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (193, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (194, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (194, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (194, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (195, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (195, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (195, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (196, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (196, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (196, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (197, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (197, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (197, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (198, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (198, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (198, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (199, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (199, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (199, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (200, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (200, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (200, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (201, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (201, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (201, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (202, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (202, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (202, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (203, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (203, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (203, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (204, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (204, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (204, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (205, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (205, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (205, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (206, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (206, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (206, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (207, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (207, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (207, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (208, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (208, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (208, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (209, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (209, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (209, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (210, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (210, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (210, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (211, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (211, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (211, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (212, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (212, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (212, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (213, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (213, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (213, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (214, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (214, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (214, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (215, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (215, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (215, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (216, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (216, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (216, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (217, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (217, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (217, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (218, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (218, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (218, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (219, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (219, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (219, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (220, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (220, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (220, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (221, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (221, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (221, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (222, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (222, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (222, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (223, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (223, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (223, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (224, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (224, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (224, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (225, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (225, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (225, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (226, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (226, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (226, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (227, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (227, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (227, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (228, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (228, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (228, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (229, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (229, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (229, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (230, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (230, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (230, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (231, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (231, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (231, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (232, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (232, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (232, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (233, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (233, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (233, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (234, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (234, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (234, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (235, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (235, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (235, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (236, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (236, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (236, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (237, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (237, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (237, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (238, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (238, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (238, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (239, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (239, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (239, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (240, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (240, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (240, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (241, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (241, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (241, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (242, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (242, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (242, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (243, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (243, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (243, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (244, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (244, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (244, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (245, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (245, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (245, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (246, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (246, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (246, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (247, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (247, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (247, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (248, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (248, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (248, 3, 2);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (1, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (2, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (3, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (4, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (5, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (6, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (7, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (8, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (9, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (10, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (11, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (12, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (13, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (14, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (15, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (16, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (17, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (18, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (19, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (20, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (21, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (22, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (23, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (24, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (25, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (26, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (27, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (28, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (29, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (30, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (31, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (32, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (33, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (34, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (35, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (36, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (37, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (38, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (39, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (40, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (41, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (42, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (43, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (44, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (45, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (46, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (47, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (48, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (49, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (50, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (51, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (52, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (53, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (54, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (55, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (56, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (57, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (58, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (59, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (60, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (61, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (62, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (63, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (64, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (65, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (66, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (67, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (68, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (69, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (70, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (71, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (72, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (73, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (74, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (75, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (76, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (77, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (78, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (79, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (80, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (81, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (82, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (83, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (84, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (85, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (86, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (87, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (88, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (89, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (90, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (91, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (92, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (93, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (94, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (95, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (96, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (97, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (98, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (99, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (100, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (101, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (102, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (103, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (104, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (105, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (106, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (107, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (108, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (109, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (110, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (111, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (112, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (113, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (114, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (115, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (116, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (117, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (118, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (119, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (120, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (121, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (122, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (123, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (124, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (125, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (126, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (127, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (128, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (129, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (130, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (131, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (132, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (133, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (134, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (135, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (136, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (137, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (138, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (139, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (140, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (141, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (142, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (143, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (144, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (145, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (146, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (147, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (148, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (149, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (150, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (151, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (152, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (153, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (154, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (155, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (156, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (157, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (158, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (159, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (160, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (161, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (162, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (163, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (164, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (165, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (166, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (167, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (168, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (169, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (170, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (171, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (172, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (173, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (174, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (175, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (176, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (177, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (178, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (179, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (180, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (181, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (182, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (183, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (184, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (185, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (186, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (187, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (188, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (189, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (190, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (191, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (192, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (193, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (194, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (195, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (196, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (197, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (198, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (199, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (200, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (201, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (202, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (203, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (204, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (205, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (206, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (207, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (208, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (209, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (210, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (211, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (212, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (213, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (214, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (215, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (216, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (217, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (218, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (219, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (220, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (221, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (222, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (223, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (224, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (225, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (226, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (227, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (228, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (229, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (230, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (231, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (232, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (233, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (234, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (235, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (236, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (237, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (238, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (239, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (240, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (241, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (242, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (243, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (244, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (245, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (246, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (247, 1, 1);

INSERT INTO character_learning (character_id, recognition_status_id, production_status_id) VALUES (248, 1, 1);

INSERT INTO library_text (id, category_id, author, period, title, body, notes) VALUES (1, 1, '张继', '唐朝', '枫桥夜泊', '月落乌啼霜满天，江枫渔火对愁眠。
姑苏城外寒山寺，夜半钟声到客船。', NULL);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (1, 1, 174);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (2, 1, 41);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (3, 1, 175);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (3, 2, 175);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (4, 1, 74);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (5, 1, 186);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (5, 2, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (6, 1, 187);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (7, 1, 59);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (8, 1, 54);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (8, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (9, 1, 157);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (9, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (10, 1, 153);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (11, 1, 226);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (12, 1, 35);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (12, 2, 109);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (13, 1, 185);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (14, 1, 6);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (15, 1, 6);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (15, 2, 110);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (15, 3, 166);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (16, 1, 6);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (16, 2, 208);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (17, 1, 204);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (18, 1, 203);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (19, 1, 80);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (20, 1, 224);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (20, 2, 117);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (21, 1, 225);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (22, 1, 69);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (23, 1, 50);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (23, 2, 193);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (23, 3, 225);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (24, 1, 194);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (25, 1, 136);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (25, 2, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (25, 3, 214);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (26, 1, 94);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (27, 1, 94);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (27, 2, 111);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (28, 1, 94);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (28, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (29, 1, 94);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (29, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (29, 3, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (30, 1, 52);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (31, 1, 188);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (32, 1, 124);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (32, 2, 124);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (33, 1, 195);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (34, 1, 172);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (35, 1, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (35, 2, 214);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (36, 1, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (36, 2, 201);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (37, 1, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (37, 2, 210);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (38, 1, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (38, 2, 125);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (39, 1, 183);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (39, 2, 125);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (39, 3, 237);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (40, 1, 122);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (41, 1, 7);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (41, 2, 207);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (42, 1, 231);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (43, 1, 218);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (44, 1, 218);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (44, 2, 15);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (45, 1, 112);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (46, 1, 112);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (46, 2, 6);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (46, 3, 223);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (47, 1, 93);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (48, 1, 93);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (48, 2, 114);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (49, 1, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (49, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (50, 1, 19);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (51, 1, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (52, 1, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (52, 2, 122);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (53, 1, 134);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (53, 2, 236);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (54, 1, 244);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (54, 2, 154);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (55, 1, 241);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (55, 2, 119);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (56, 1, 51);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (57, 1, 51);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (57, 2, 233);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (58, 1, 247);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (58, 2, 45);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (59, 1, 78);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (59, 2, 78);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (60, 1, 164);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (61, 1, 9);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (62, 1, 198);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (63, 1, 116);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (63, 2, 33);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (64, 1, 42);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (64, 2, 68);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (65, 1, 177);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (66, 1, 222);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (67, 1, 87);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (68, 1, 227);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (69, 1, 107);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (69, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (70, 1, 168);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (70, 2, 215);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (71, 1, 168);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (71, 2, 105);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (72, 1, 100);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (73, 1, 100);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (73, 2, 69);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (74, 1, 100);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (74, 2, 189);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (75, 1, 100);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (75, 2, 75);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (76, 1, 100);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (76, 2, 179);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (76, 3, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (77, 1, 67);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (78, 1, 84);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (79, 1, 77);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (80, 1, 126);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (81, 1, 72);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (82, 1, 86);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (83, 1, 31);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (84, 1, 171);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (84, 2, 225);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (85, 1, 248);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (85, 2, 205);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (86, 1, 49);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (87, 1, 111);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (88, 1, 111);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (88, 2, 23);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (89, 1, 209);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (90, 1, 29);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (91, 1, 246);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (91, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (92, 1, 65);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (93, 1, 103);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (93, 2, 103);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (94, 1, 25);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (94, 2, 120);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (95, 1, 25);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (95, 2, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (96, 1, 12);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (97, 1, 211);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (97, 2, 127);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (98, 1, 123);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (99, 1, 123);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (99, 2, 225);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (100, 1, 189);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (101, 1, 189);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (101, 2, 185);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (102, 1, 189);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (102, 2, 209);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (103, 1, 66);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (103, 2, 27);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (104, 1, 219);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (105, 1, 63);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (106, 1, 90);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (107, 1, 156);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (108, 1, 199);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (108, 2, 118);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (109, 1, 17);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (110, 1, 48);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (111, 1, 232);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (112, 1, 8);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (113, 1, 240);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (114, 1, 43);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (115, 1, 101);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (115, 2, 101);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (116, 1, 73);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (117, 1, 16);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (118, 1, 60);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (119, 1, 128);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (120, 1, 178);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (121, 1, 169);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (121, 2, 44);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (121, 3, 197);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (122, 1, 169);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (122, 2, 149);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (123, 1, 102);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (123, 2, 102);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (124, 1, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (125, 1, 196);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (125, 2, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (126, 1, 242);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (126, 2, 54);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (127, 1, 242);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (127, 2, 155);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (127, 3, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (128, 1, 71);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (128, 2, 105);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (129, 1, 143);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (129, 2, 120);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (130, 1, 143);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (130, 2, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (131, 1, 79);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (132, 1, 79);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (132, 2, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (133, 1, 79);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (133, 2, 232);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (134, 1, 79);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (134, 2, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (135, 1, 230);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (136, 1, 230);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (136, 2, 226);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (137, 1, 230);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (137, 2, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (138, 1, 230);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (138, 2, 232);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (139, 1, 230);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (139, 2, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (140, 1, 184);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (141, 1, 184);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (141, 2, 150);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (141, 3, 62);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (142, 1, 76);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (143, 1, 200);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (144, 1, 34);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (145, 1, 34);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (145, 2, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (146, 1, 120);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (147, 1, 131);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (148, 1, 176);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (148, 2, 98);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (149, 1, 97);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (150, 1, 97);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (150, 2, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (151, 1, 97);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (151, 2, 150);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (151, 3, 62);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (152, 1, 97);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (152, 2, 91);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (153, 1, 150);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (153, 2, 62);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (154, 1, 170);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (154, 2, 22);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (155, 1, 202);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (155, 2, 158);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (156, 1, 2);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (157, 1, 223);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (157, 2, 121);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (158, 1, 57);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (159, 1, 53);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (160, 1, 234);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (161, 1, 217);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (162, 1, 217);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (162, 2, 235);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (163, 1, 61);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (164, 1, 61);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (164, 2, 120);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (165, 1, 173);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (166, 1, 23);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (167, 1, 212);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (167, 2, 213);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (168, 1, 140);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (169, 1, 3);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (170, 1, 81);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (170, 2, 122);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (171, 1, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (172, 1, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (172, 2, 181);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (173, 1, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (173, 2, 219);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (174, 1, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (174, 2, 58);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (175, 1, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (175, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (176, 1, 114);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (177, 1, 24);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (177, 2, 11);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (178, 1, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (178, 2, 185);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (179, 1, 56);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (180, 1, 142);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (180, 2, 36);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (181, 1, 142);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (181, 2, 236);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (182, 1, 18);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (183, 1, 146);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (184, 1, 135);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (184, 2, 154);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (185, 1, 15);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (186, 1, 15);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (186, 2, 122);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (187, 1, 220);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (188, 1, 167);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (189, 1, 167);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (189, 2, 158);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (190, 1, 191);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (191, 1, 191);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (191, 2, 211);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (192, 1, 216);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (193, 1, 216);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (193, 2, 214);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (194, 1, 85);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (195, 1, 115);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (196, 1, 26);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (197, 1, 26);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (197, 2, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (198, 1, 108);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (199, 1, 108);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (199, 2, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (200, 1, 99);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (201, 1, 99);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (201, 2, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (202, 1, 96);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (203, 1, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (204, 1, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (204, 2, 166);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (205, 1, 75);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (206, 1, 75);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (206, 2, 209);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (207, 1, 70);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (207, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (208, 1, 92);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (209, 1, 92);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (209, 2, 226);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (210, 1, 179);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (211, 1, 147);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (212, 1, 147);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (212, 2, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (213, 1, 147);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (213, 2, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (214, 1, 82);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (215, 1, 235);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (216, 1, 235);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (216, 2, 243);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (217, 1, 133);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (218, 1, 133);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (218, 2, 28);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (219, 1, 20);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (220, 1, 58);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (220, 2, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (221, 1, 83);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (221, 2, 163);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (222, 1, 5);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (223, 1, 5);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (223, 2, 181);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (224, 1, 5);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (224, 2, 219);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (225, 1, 5);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (225, 2, 58);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (226, 1, 5);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (226, 2, 238);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (227, 1, 40);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (227, 2, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (228, 1, 180);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (228, 2, 88);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (229, 1, 132);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (230, 1, 113);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (231, 1, 113);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (231, 2, 150);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (231, 3, 62);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (232, 1, 113);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (232, 2, 142);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (233, 1, 113);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (233, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (234, 1, 113);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (234, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (234, 3, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (235, 1, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (236, 1, 47);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (237, 1, 221);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (237, 2, 221);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (238, 1, 139);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (239, 1, 144);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (239, 2, 152);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (240, 1, 144);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (240, 2, 152);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (240, 3, 140);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (241, 1, 144);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (241, 2, 152);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (241, 3, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (242, 1, 30);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (242, 2, 130);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (243, 1, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (244, 1, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (244, 2, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (245, 1, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (245, 2, 14);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (246, 1, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (246, 2, 159);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (247, 1, 239);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (248, 1, 208);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (249, 1, 13);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (250, 1, 1);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (251, 1, 1);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (251, 2, 59);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (252, 1, 1);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (252, 2, 172);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (252, 3, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (253, 1, 1);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (253, 2, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (254, 1, 206);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (254, 2, 151);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (255, 1, 55);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (255, 2, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (256, 1, 55);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (256, 2, 237);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (257, 1, 162);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (257, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (258, 1, 149);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (259, 1, 149);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (259, 2, 188);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (260, 1, 149);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (260, 2, 172);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (260, 3, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (261, 1, 149);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (261, 2, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (262, 1, 238);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (263, 1, 39);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (264, 1, 148);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (265, 1, 46);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (266, 1, 46);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (266, 2, 209);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (267, 1, 88);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (268, 1, 141);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (269, 1, 141);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (269, 2, 245);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (270, 1, 141);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (270, 2, 4);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (271, 1, 129);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (271, 2, 11);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (272, 1, 129);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (272, 2, 11);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (272, 3, 160);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (273, 1, 137);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (274, 1, 228);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (275, 1, 228);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (275, 2, 226);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (276, 1, 228);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (276, 2, 38);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (277, 1, 228);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (277, 2, 232);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (278, 1, 228);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (278, 2, 21);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (279, 1, 190);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (280, 1, 165);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (280, 2, 88);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (281, 1, 192);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (281, 2, 229);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (282, 1, 64);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (283, 1, 10);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (283, 2, 87);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (284, 1, 10);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (284, 2, 138);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (285, 1, 10);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (285, 2, 58);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (286, 1, 10);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (286, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (287, 1, 10);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (287, 2, 106);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (287, 3, 182);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (288, 1, 32);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (289, 1, 161);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (289, 2, 104);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (290, 1, 105);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (291, 1, 145);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (291, 2, 95);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (292, 1, 89);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (293, 1, 37);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (294, 1, 37);

INSERT INTO vocabulary_character (vocabulary_id, position, character_id) VALUES (294, 2, 245);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (1, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (1, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (1, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (2, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (2, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (2, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (3, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (3, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (3, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (4, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (4, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (4, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (5, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (5, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (6, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (6, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (6, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (7, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (7, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (7, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (8, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (8, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (8, 3, 3, 5);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (9, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (9, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (9, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (10, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (10, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (10, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (11, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (11, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (12, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (12, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (12, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (13, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (13, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (14, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (14, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (14, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (15, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (15, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (15, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (16, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (16, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (17, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (17, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (17, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (18, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (18, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (18, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (19, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (19, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (20, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (20, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (20, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (21, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (21, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (22, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (22, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (22, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (23, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (23, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (23, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (24, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (24, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (24, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (25, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (25, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (25, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (26, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (26, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (26, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (27, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (27, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (27, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (28, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (28, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (29, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (29, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (30, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (30, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (30, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (31, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (31, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (31, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (32, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (32, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (32, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (33, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (33, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (34, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (34, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (34, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (35, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (35, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (36, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (36, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (36, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (37, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (37, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (37, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (38, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (38, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (38, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (39, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (39, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (40, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (40, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (41, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (41, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (41, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (42, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (42, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (42, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (43, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (43, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (43, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (44, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (44, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (45, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (45, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (45, 3, 3, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (45, 4, 3, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (46, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (46, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (46, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (47, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (47, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (47, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (48, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (48, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (48, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (49, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (49, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (49, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (50, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (50, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (50, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (51, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (51, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (52, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (52, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (53, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (53, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (53, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (54, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (54, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (54, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (55, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (55, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (55, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (56, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (56, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (56, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (57, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (57, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (57, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (58, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (58, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (58, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (59, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (59, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (59, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (60, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (60, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (61, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (61, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (61, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (62, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (62, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (62, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (63, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (63, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (63, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (64, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (64, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (64, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (65, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (65, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (65, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (66, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (66, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (66, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (67, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (67, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (68, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (68, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (68, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (68, 4, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (69, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (69, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (69, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (70, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (70, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (70, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (71, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (71, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (72, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (72, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (72, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (73, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (73, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (73, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (74, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (74, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (75, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (75, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (76, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (76, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (77, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (77, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (77, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (78, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (78, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (78, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (79, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (79, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (79, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (80, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (80, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (80, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (81, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (81, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (82, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (82, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (82, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (83, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (83, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (83, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (84, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (84, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (85, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (85, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (85, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (86, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (86, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (86, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (87, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (87, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (87, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (88, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (88, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (89, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (89, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (90, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (90, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (90, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (91, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (91, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (91, 3, 3, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (92, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (92, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (92, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (93, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (93, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (93, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (94, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (94, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (95, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (95, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (95, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (96, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (96, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (96, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (97, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (97, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (97, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (98, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (98, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (98, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (99, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (99, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (100, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (100, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (100, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (101, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (101, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (102, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (102, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (102, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (103, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (103, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (103, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (104, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (104, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (104, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (105, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (105, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (105, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (106, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (106, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (106, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (107, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (107, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (107, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (108, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (108, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (108, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (109, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (109, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (109, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (110, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (110, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (110, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (111, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (111, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (111, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (112, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (112, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (112, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (113, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (113, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (113, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (114, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (114, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (114, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (115, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (115, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (115, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (116, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (116, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (116, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (117, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (117, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (117, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (118, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (118, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (118, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (119, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (119, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (119, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (120, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (120, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (120, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (121, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (121, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (121, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (122, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (122, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (123, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (123, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (123, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (124, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (124, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (125, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (125, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (125, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (126, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (126, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (126, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (127, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (127, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (128, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (128, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (128, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (129, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (129, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (130, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (130, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (130, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (131, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (131, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (131, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (132, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (132, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (133, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (133, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (134, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (134, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (135, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (135, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (135, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (136, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (136, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (137, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (137, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (138, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (138, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (139, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (139, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (140, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (140, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (141, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (141, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (142, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (142, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (142, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (143, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (143, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (143, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (144, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (144, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (144, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (145, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (145, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (146, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (146, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (146, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (147, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (147, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (147, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (148, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (148, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (148, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (149, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (149, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (150, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (150, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (150, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (151, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (151, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (152, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (152, 2, 1, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (152, 3, 3, 5);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (153, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (153, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (153, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (154, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (154, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (154, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (155, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (155, 2, 1, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (155, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (156, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (156, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (156, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (157, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (157, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (157, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (158, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (158, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (158, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (159, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (159, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (160, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (160, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (160, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (161, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (161, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (161, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (162, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (162, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (163, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (163, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (163, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (164, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (164, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (164, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (165, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (165, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (165, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (166, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (166, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (166, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (167, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (167, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (167, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (168, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (168, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (168, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (169, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (169, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (169, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (170, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (170, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (170, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (171, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (171, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (171, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (172, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (172, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (172, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (173, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (173, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (174, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (174, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (174, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (175, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (175, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (176, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (176, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (176, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (177, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (177, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (177, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (178, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (178, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (178, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (179, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (179, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (179, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (180, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (180, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (180, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (181, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (181, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (181, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (182, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (182, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (183, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (183, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (183, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (184, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (184, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (184, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (185, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (185, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (185, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (186, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (186, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (187, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (187, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (187, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (188, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (188, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (188, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (189, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (189, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (189, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (190, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (190, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (191, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (191, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (191, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (192, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (192, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (193, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (193, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (193, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (194, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (194, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (194, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (195, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (195, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (195, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (196, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (196, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (196, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (197, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (197, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (198, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (198, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (198, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (199, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (199, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (200, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (200, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (200, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (201, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (201, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (202, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (202, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (202, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (203, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (203, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (204, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (204, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (204, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (205, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (205, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (205, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (206, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (206, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (207, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (207, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (207, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (208, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (208, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (208, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (209, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (209, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (210, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (210, 2, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (211, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (211, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (212, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (212, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (213, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (213, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (213, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (214, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (214, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (214, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (215, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (215, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (215, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (216, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (216, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (216, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (217, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (217, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (217, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (218, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (218, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (218, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (219, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (219, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (219, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (220, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (220, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (221, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (221, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (221, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (222, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (222, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (222, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (223, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (223, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (224, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (224, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (225, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (225, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (225, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (226, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (226, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (226, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (227, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (227, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (227, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (228, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (228, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (228, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (229, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (229, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (229, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (230, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (230, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (230, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (231, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (231, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (232, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (232, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (232, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (233, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (233, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (234, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (234, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (235, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (235, 2, 1, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (235, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (236, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (236, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (236, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (237, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (237, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (237, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (238, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (238, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (238, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (239, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (239, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (239, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (240, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (240, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (241, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (241, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (242, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (242, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (242, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (243, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (243, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (244, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (244, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (244, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (245, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (245, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (245, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (246, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (246, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (246, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (247, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (247, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (247, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (248, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (248, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (248, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (249, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (249, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (249, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (250, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (250, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (250, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (251, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (251, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (252, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (252, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (253, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (253, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (254, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (254, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (254, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (255, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (255, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (255, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (256, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (256, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (256, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (257, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (257, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (257, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (258, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (258, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (258, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (259, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (259, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (260, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (260, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (261, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (261, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (262, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (262, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (263, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (263, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (263, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (264, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (264, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (264, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (265, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (265, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (265, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (266, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (266, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (266, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (267, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (267, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (267, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (268, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (268, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (269, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (269, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (270, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (270, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (270, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (271, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (271, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (271, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (272, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (272, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (272, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (273, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (273, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (273, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (274, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (274, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (274, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (275, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (275, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (276, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (276, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (277, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (277, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (278, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (278, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (279, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (279, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (279, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (280, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (280, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (280, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (281, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (281, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (281, 3, 3, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (282, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (282, 2, 1, 2);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (282, 3, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (282, 4, 3, 3);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (283, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (283, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (283, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (284, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (284, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (284, 3, 3, 4);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (285, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (285, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (285, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (286, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (286, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (287, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (287, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (288, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (288, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (288, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (289, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (289, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (289, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (290, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (290, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (290, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (291, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (291, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (291, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (292, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (292, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (292, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (293, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (293, 2, 1, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (293, 3, 3, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (294, 1, 2, 1);

INSERT INTO vocabulary_hsk_level (vocabulary_id, position, hsk_scheme_id, level) VALUES (294, 2, 1, 2);

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (1, 1, 1, '愛', 'ài', 'ai4', 'ai⁴', 'ㄞˋ', 'ay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (2, 2, 1, '八', 'bā', 'ba1', 'pa¹', 'ㄅㄚ', 'ba');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (3, 3, 1, '爸爸', 'bà ba', 'ba4 ba5', 'pa⁴ ba', 'ㄅㄚˋ ㄅㄚ˙', 'bah ba');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (4, 4, 1, '吧', 'bā', 'ba1', 'pa¹', 'ㄅㄚ', 'ba');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (5, 4, 2, '吧', 'ba', 'ba5', 'ba', 'ㄅㄚ˙', 'ba');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (6, 4, 3, '吧', 'biā', 'bia1', 'biā', 'ㄅㄧㄚ', 'biā');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (7, 5, 1, '白天', 'bái tiān', 'bai2 tian1', 'pai² t''ien¹', 'ㄅㄞˊ ㄊㄧㄢ', 'bair tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (8, 6, 1, '百', 'Bǎi', 'Bai3', 'pai³', 'ㄅㄞˇ', 'bae');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (9, 6, 2, '百', 'bǎi', 'bai3', 'pai³', 'ㄅㄞˇ', 'bae');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (10, 7, 1, '半', 'bàn', 'ban4', 'pan⁴', 'ㄅㄢˋ', 'bann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (11, 8, 1, '包子', 'bāo zi', 'bao1 zi5', 'pao¹ zi', 'ㄅㄠ ㄗ˙', 'bau zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (12, 9, 1, '杯子', 'bēi zi', 'bei1 zi5', 'pei¹ zi', 'ㄅㄟ ㄗ˙', 'bei zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (13, 10, 1, '本', 'běn', 'ben3', 'pen³', 'ㄅㄣˇ', 'been');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (14, 11, 1, '邊', 'biān', 'bian1', 'pien¹', 'ㄅㄧㄢ', 'bian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (15, 11, 2, '邊', 'bian', 'bian5', 'bian', 'ㄅㄧㄢ˙', 'bian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (16, 12, 1, '便宜', 'biàn yí', 'bian4 yi2', 'pien⁴ i²', 'ㄅㄧㄢˋ ㄧˊ', 'biann yi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (17, 12, 2, '便宜', 'pián yi', 'pian2 yi5', 'p''ien² yi', 'ㄆㄧㄢˊ ㄧ˙', 'pyan yi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (18, 13, 1, '病', 'bìng', 'bing4', 'ping⁴', 'ㄅㄧㄥˋ', 'binq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (19, 14, 1, '不', 'bù', 'bu4', 'pu⁴', 'ㄅㄨˋ', 'buh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (20, 15, 1, '不客氣', 'bù kè qi', 'bu4 ke4 qi5', 'pu⁴ k''o⁴ qi', 'ㄅㄨˋ ㄎㄜˋ ㄑㄧ˙', 'buh keh qi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (21, 16, 1, '不要', 'bù yào', 'bu4 yao4', 'pu⁴ yao⁴', 'ㄅㄨˋ ㄧㄠˋ', 'buh yaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (22, 17, 1, '菜', 'cài', 'cai4', 'ts''ai⁴', 'ㄘㄞˋ', 'tsay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (23, 18, 1, '茶', 'chá', 'cha2', 'ch''a²', 'ㄔㄚˊ', 'char');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (24, 19, 1, '唱', 'chàng', 'chang4', 'ch''ang⁴', 'ㄔㄤˋ', 'chanq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (25, 20, 1, '超市', 'chāo shì', 'chao1 shi4', 'ch''ao¹ shih⁴', 'ㄔㄠ ㄕˋ', 'chau shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (26, 21, 1, '車', 'Chē', 'Che1', 'ch''e¹', 'ㄔㄜ', 'che');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (27, 21, 2, '車', 'chē', 'che1', 'ch''e¹', 'ㄔㄜ', 'che');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (28, 21, 3, '車', 'jū', 'ju1', 'chü¹', 'ㄐㄩ', 'jiu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (29, 22, 1, '吃', 'chī', 'chi1', 'ch''ih¹', 'ㄔ', 'chy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (30, 22, 2, '喫', 'chī', 'chi1', 'ch''ih¹', 'ㄔ', 'chy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (31, 23, 1, '出租車', 'chū zū chē', 'chu1 zu1 che1', 'ch''u¹ tsu¹ ch''e¹', 'ㄔㄨ ㄗㄨ ㄔㄜ', 'chu tzu che');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (32, 24, 1, '穿', 'chuān', 'chuan1', 'ch''uan¹', 'ㄔㄨㄢ', 'chuan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (33, 25, 1, '打電話', 'dǎ diàn huà', 'da3 dian4 hua4', 'ta³ tien⁴ hua⁴', 'ㄉㄚˇ ㄉㄧㄢˋ ㄏㄨㄚˋ', 'daa diann huah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (34, 26, 1, '大', 'dà', 'da4', 'ta⁴', 'ㄉㄚˋ', 'dah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (35, 26, 2, '大', 'dài', 'dai4', 'tai⁴', 'ㄉㄞˋ', 'day');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (36, 27, 1, '大家', 'dà jiā', 'da4 jia1', 'ta⁴ chia¹', 'ㄉㄚˋ ㄐㄧㄚ', 'dah jia');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (37, 28, 1, '大學', 'Dà xué', 'Da4 xue2', 'ta⁴ hsüeh²', 'ㄉㄚˋ ㄒㄩㄝˊ', 'dah shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (38, 28, 2, '大學', 'dà xué', 'da4 xue2', 'ta⁴ hsüeh²', 'ㄉㄚˋ ㄒㄩㄝˊ', 'dah shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (39, 29, 1, '大學生', 'dà xué shēng', 'da4 xue2 sheng1', 'ta⁴ hsüeh² sheng¹', 'ㄉㄚˋ ㄒㄩㄝˊ ㄕㄥ', 'dah shyue sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (40, 30, 1, '到', 'dào', 'dao4', 'tao⁴', 'ㄉㄠˋ', 'daw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (41, 31, 1, '的', 'de', 'de5', 'de', 'ㄉㄜ˙', 'de');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (42, 31, 2, '的', 'dī', 'di1', 'ti¹', 'ㄉㄧ', 'di');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (43, 31, 3, '的', 'dí', 'di2', 'ti²', 'ㄉㄧˊ', 'dyi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (44, 31, 4, '的', 'dì', 'di4', 'ti⁴', 'ㄉㄧˋ', 'dih');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (45, 32, 1, '弟弟', 'dì di', 'di4 di5', 'ti⁴ di', 'ㄉㄧˋ ㄉㄧ˙', 'dih di');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (46, 33, 1, '第', 'dì', 'di4', 'ti⁴', 'ㄉㄧˋ', 'dih');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (47, 34, 1, '點', 'diǎn', 'dian3', 'tien³', 'ㄉㄧㄢˇ', 'dean');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (48, 35, 1, '電話', 'diàn huà', 'dian4 hua4', 'tien⁴ hua⁴', 'ㄉㄧㄢˋ ㄏㄨㄚˋ', 'diann huah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (49, 36, 1, '電腦', 'diàn nǎo', 'dian4 nao3', 'tien⁴ nao³', 'ㄉㄧㄢˋ ㄋㄠˇ', 'diann nao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (50, 37, 1, '電視', 'diàn shì', 'dian4 shi4', 'tien⁴ shih⁴', 'ㄉㄧㄢˋ ㄕˋ', 'diann shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (51, 38, 1, '電影', 'diàn yǐng', 'dian4 ying3', 'tien⁴ ying³', 'ㄉㄧㄢˋ ㄧㄥˇ', 'diann yiing');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (52, 39, 1, '電影院', 'diàn yǐng yuàn', 'dian4 ying3 yuan4', 'tien⁴ ying³ yüan⁴', 'ㄉㄧㄢˋ ㄧㄥˇ ㄩㄢˋ', 'diann yiing yuann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (53, 40, 1, '店', 'diàn', 'dian4', 'tien⁴', 'ㄉㄧㄢˋ', 'diann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (54, 41, 1, '東西', 'dōng xī', 'dong1 xi1', 'tung¹ hsi¹', 'ㄉㄨㄥ ㄒㄧ', 'dong shi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (55, 41, 2, '東西', 'dōng xi', 'dong1 xi5', 'tung¹ xi', 'ㄉㄨㄥ ㄒㄧ˙', 'dong xi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (56, 42, 1, '都', 'Dū', 'Du1', 'tu¹', 'ㄉㄨ', 'du');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (57, 42, 2, '都', 'dōu', 'dou1', 'tou¹', 'ㄉㄡ', 'dou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (58, 42, 3, '都', 'dū', 'du1', 'tu¹', 'ㄉㄨ', 'du');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (59, 43, 1, '讀', 'dòu', 'dou4', 'tou⁴', 'ㄉㄡˋ', 'dow');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (60, 43, 2, '讀', 'dú', 'du2', 'tu²', 'ㄉㄨˊ', 'dwu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (61, 44, 1, '讀書', 'dú shū', 'du2 shu1', 'tu² shu¹', 'ㄉㄨˊ ㄕㄨ', 'dwu shu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (62, 45, 1, '對', 'duì', 'dui4', 'tui⁴', 'ㄉㄨㄟˋ', 'duey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (63, 46, 1, '對不起', 'duì bu qǐ', 'dui4 bu5 qi3', 'tui⁴ bu ch''i³', 'ㄉㄨㄟˋ ㄅㄨ˙ ㄑㄧˇ', 'duey bu chii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (64, 47, 1, '多', 'duō', 'duo1', 'to¹', 'ㄉㄨㄛ', 'duo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (65, 48, 1, '多少', 'duō shǎo', 'duo1 shao3', 'to¹ shao³', 'ㄉㄨㄛ ㄕㄠˇ', 'duo shao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (66, 48, 2, '多少', 'duō shao', 'duo1 shao5', 'to¹ shao', 'ㄉㄨㄛ ㄕㄠ˙', 'duo shao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (67, 49, 1, '兒子', 'ér zi', 'er2 zi5', 'erh² zi', 'ㄦˊ ㄗ˙', 'erl zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (68, 50, 1, '二', 'èr', 'er4', 'erh⁴', 'ㄦˋ', 'ell');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (69, 51, 1, '飯', 'fàn', 'fan4', 'fan⁴', 'ㄈㄢˋ', 'fann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (70, 52, 1, '飯店', 'fàn diàn', 'fan4 dian4', 'fan⁴ tien⁴', 'ㄈㄢˋ ㄉㄧㄢˋ', 'fann diann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (71, 53, 1, '房間', 'fáng jiān', 'fang2 jian1', 'fang² chien¹', 'ㄈㄤˊ ㄐㄧㄢ', 'farng jian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (72, 54, 1, '飛機', 'fēi jī', 'fei1 ji1', 'fei¹ chi¹', 'ㄈㄟ ㄐㄧ', 'fei ji');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (73, 55, 1, '非常', 'fēi cháng', 'fei1 chang2', 'fei¹ ch''ang²', 'ㄈㄟ ㄔㄤˊ', 'fei charng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (74, 56, 1, '分', 'fēn', 'fen1', 'fen¹', 'ㄈㄣ', 'fen');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (75, 56, 2, '分', 'fèn', 'fen4', 'fen⁴', 'ㄈㄣˋ', 'fenn');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (76, 57, 1, '分鐘', 'fēn zhōng', 'fen1 zhong1', 'fen¹ chung¹', 'ㄈㄣ ㄓㄨㄥ', 'fen jong');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (77, 58, 1, '高興', 'gāo xìng', 'gao1 xing4', 'kao¹ hsing⁴', 'ㄍㄠ ㄒㄧㄥˋ', 'gau shinq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (78, 59, 1, '哥哥', 'gē ge', 'ge1 ge5', 'ko¹ ge', 'ㄍㄜ ㄍㄜ˙', 'ge ge');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (79, 60, 1, '歌', 'gē', 'ge1', 'ko¹', 'ㄍㄜ', 'ge');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (80, 60, 2, '謌', 'gē', 'ge1', 'ko¹', 'ㄍㄜ', 'ge');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (81, 61, 1, '個', 'gě', 'ge3', 'ko³', 'ㄍㄜˇ', 'gee');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (82, 61, 2, '個', 'gè', 'ge4', 'ko⁴', 'ㄍㄜˋ', 'geh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (83, 61, 3, '箇', 'gè', 'ge4', 'ko⁴', 'ㄍㄜˋ', 'geh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (84, 62, 1, '給', 'gěi', 'gei3', 'kei³', 'ㄍㄟˇ', 'geei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (85, 62, 2, '給', 'jǐ', 'ji3', 'chi³', 'ㄐㄧˇ', 'jii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (86, 63, 1, '工作', 'gōng zuò', 'gong1 zuo4', 'kung¹ tso⁴', 'ㄍㄨㄥ ㄗㄨㄛˋ', 'gong tzuoh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (87, 64, 1, '公司', 'gōng sī', 'gong1 si1', 'kung¹ ssu¹', 'ㄍㄨㄥ ㄙ', 'gong sy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (88, 65, 1, '狗', 'gǒu', 'gou3', 'kou³', 'ㄍㄡˇ', 'goou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (89, 66, 1, '貴', 'guì', 'gui4', 'kuei⁴', 'ㄍㄨㄟˋ', 'guey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (90, 67, 1, '國', 'Guó', 'Guo2', 'kuo²', 'ㄍㄨㄛˊ', 'gwo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (91, 67, 2, '國', 'guó', 'guo2', 'kuo²', 'ㄍㄨㄛˊ', 'gwo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (92, 68, 1, '還', 'Huán', 'Huan2', 'huan²', 'ㄏㄨㄢˊ', 'hwan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (93, 68, 2, '還', 'hái', 'hai2', 'hai²', 'ㄏㄞˊ', 'hair');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (94, 68, 3, '還', 'huán', 'huan2', 'huan²', 'ㄏㄨㄢˊ', 'hwan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (95, 69, 1, '孩子', 'hái zi', 'hai2 zi5', 'hai² zi', 'ㄏㄞˊ ㄗ˙', 'hair zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (96, 70, 1, '漢語', 'Hàn yǔ', 'Han4 yu3', 'han⁴ yü³', 'ㄏㄢˋ ㄩˇ', 'hann yeu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (97, 71, 1, '漢字', 'hàn zì', 'han4 zi4', 'han⁴ tzu⁴', 'ㄏㄢˋ ㄗˋ', 'hann tzyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (98, 72, 1, '好', 'hǎo', 'hao3', 'hao³', 'ㄏㄠˇ', 'hao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (99, 72, 2, '好', 'hào', 'hao4', 'hao⁴', 'ㄏㄠˋ', 'haw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (100, 73, 1, '好吃', 'hǎo chī', 'hao3 chi1', 'hao³ ch''ih¹', 'ㄏㄠˇ ㄔ', 'hao chy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (101, 73, 2, '好吃', 'hào chī', 'hao4 chi1', 'hao⁴ ch''ih¹', 'ㄏㄠˋ ㄔ', 'haw chy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (102, 74, 1, '好看', 'hǎo kàn', 'hao3 kan4', 'hao³ k''an⁴', 'ㄏㄠˇ ㄎㄢˋ', 'hao kann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (103, 75, 1, '好聽', 'hǎo tīng', 'hao3 ting1', 'hao³ t''ing¹', 'ㄏㄠˇ ㄊㄧㄥ', 'hao ting');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (104, 76, 1, '好玩兒', 'hǎo wán r', 'hao3 wan2 r5', 'hao³ wan² r', 'ㄏㄠˇ ㄨㄢˊ ㄦ˙', 'hao wan r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (105, 77, 1, '號', 'háo', 'hao2', 'hao²', 'ㄏㄠˊ', 'haur');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (106, 77, 2, '號', 'hào', 'hao4', 'hao⁴', 'ㄏㄠˋ', 'haw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (107, 78, 1, '喝', 'hē', 'he1', 'ho¹', 'ㄏㄜ', 'he');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (108, 78, 2, '喝', 'hè', 'he4', 'ho⁴', 'ㄏㄜˋ', 'heh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (109, 79, 1, '咊', 'hé', 'he2', 'ho²', 'ㄏㄜˊ', 'her');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (110, 79, 2, '和', 'Hé', 'He2', 'ho²', 'ㄏㄜˊ', 'her');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (111, 79, 3, '和', 'hé', 'he2', 'ho²', 'ㄏㄜˊ', 'her');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (112, 79, 4, '和', 'hè', 'he4', 'ho⁴', 'ㄏㄜˋ', 'heh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (113, 79, 5, '和', 'hú', 'hu2', 'hu²', 'ㄏㄨˊ', 'hwu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (114, 79, 6, '和', 'huó', 'huo2', 'huo²', 'ㄏㄨㄛˊ', 'hwo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (115, 79, 7, '和', 'huò', 'huo4', 'huo⁴', 'ㄏㄨㄛˋ', 'huoh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (116, 79, 8, '龢', 'hé', 'he2', 'ho²', 'ㄏㄜˊ', 'her');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (117, 80, 1, '很', 'hěn', 'hen3', 'hen³', 'ㄏㄣˇ', 'heen');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (118, 81, 1, '后', 'Hòu', 'Hou4', 'hou⁴', 'ㄏㄡˋ', 'how');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (119, 81, 2, '后', 'hòu', 'hou4', 'hou⁴', 'ㄏㄡˋ', 'how');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (120, 81, 3, '後', 'hòu', 'hou4', 'hou⁴', 'ㄏㄡˋ', 'how');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (121, 82, 1, '回', 'huí', 'hui2', 'hui²', 'ㄏㄨㄟˊ', 'hwei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (122, 82, 2, '迴', 'huí', 'hui2', 'hui²', 'ㄏㄨㄟˊ', 'hwei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (123, 82, 3, '逥', 'huí', 'hui2', 'hui²', 'ㄏㄨㄟˊ', 'hwei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (124, 83, 1, '會', 'huì', 'hui4', 'hui⁴', 'ㄏㄨㄟˋ', 'huey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (125, 83, 2, '會', 'kuài', 'kuai4', 'k''uai⁴', 'ㄎㄨㄞˋ', 'kuay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (126, 84, 1, '火車', 'huǒ chē', 'huo3 che1', 'huo³ ch''e¹', 'ㄏㄨㄛˇ ㄔㄜ', 'huoo che');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (127, 85, 1, '雞蛋', 'jī dàn', 'ji1 dan4', 'chi¹ tan⁴', 'ㄐㄧ ㄉㄢˋ', 'ji dann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (128, 86, 1, '几', 'jī', 'ji1', 'chi¹', 'ㄐㄧ', 'ji');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (129, 86, 2, '幾', 'jī', 'ji1', 'chi¹', 'ㄐㄧ', 'ji');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (130, 86, 3, '幾', 'jǐ', 'ji3', 'chi³', 'ㄐㄧˇ', 'jii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (131, 87, 1, '傢', 'jiā', 'jia1', 'chia¹', 'ㄐㄧㄚ', 'jia');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (132, 87, 2, '家', 'jiā', 'jia1', 'chia¹', 'ㄐㄧㄚ', 'jia');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (133, 88, 1, '家人', 'jiā rén', 'jia1 ren2', 'chia¹ jen²', 'ㄐㄧㄚ ㄖㄣˊ', 'jia ren');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (134, 89, 1, '見', 'jiàn', 'jian4', 'chien⁴', 'ㄐㄧㄢˋ', 'jiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (135, 89, 2, '見', 'xiàn', 'xian4', 'hsien⁴', 'ㄒㄧㄢˋ', 'shiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (136, 90, 1, '件', 'jiàn', 'jian4', 'chien⁴', 'ㄐㄧㄢˋ', 'jiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (137, 91, 1, '餃子', 'jiǎo zi', 'jiao3 zi5', 'chiao³ zi', 'ㄐㄧㄠˇ ㄗ˙', 'jeau zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (138, 92, 1, '叫', 'jiào', 'jiao4', 'chiao⁴', 'ㄐㄧㄠˋ', 'jiaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (139, 92, 2, '呌', 'jiào', 'jiao4', 'chiao⁴', 'ㄐㄧㄠˋ', 'jiaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (140, 93, 1, '姐姐', 'jiě jie', 'jie3 jie5', 'chieh³ jie', 'ㄐㄧㄝˇ ㄐㄧㄝ˙', 'jiee jie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (141, 94, 1, '今年', 'jīn nián', 'jin1 nian2', 'chin¹ nien²', 'ㄐㄧㄣ ㄋㄧㄢˊ', 'jin nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (142, 95, 1, '今天', 'jīn tiān', 'jin1 tian1', 'chin¹ t''ien¹', 'ㄐㄧㄣ ㄊㄧㄢ', 'jin tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (143, 96, 1, '九', 'jiǔ', 'jiu3', 'chiu³', 'ㄐㄧㄡˇ', 'jeou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (144, 97, 1, '覺得', 'jué de', 'jue2 de5', 'chüeh² de', 'ㄐㄩㄝˊ ㄉㄜ˙', 'jyue de');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (145, 98, 1, '開', 'kāi', 'kai1', 'k''ai¹', 'ㄎㄞ', 'kai');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (146, 99, 1, '開車', 'kāi chē', 'kai1 che1', 'k''ai¹ ch''e¹', 'ㄎㄞ ㄔㄜ', 'kai che');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (147, 100, 1, '看', 'kān', 'kan1', 'k''an¹', 'ㄎㄢ', 'kan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (148, 100, 2, '看', 'kàn', 'kan4', 'k''an⁴', 'ㄎㄢˋ', 'kann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (149, 101, 1, '看病', 'kàn bìng', 'kan4 bing4', 'k''an⁴ ping⁴', 'ㄎㄢˋ ㄅㄧㄥˋ', 'kann binq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (150, 102, 1, '看見', 'kàn jiàn', 'kan4 jian4', 'k''an⁴ chien⁴', 'ㄎㄢˋ ㄐㄧㄢˋ', 'kann jiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (151, 103, 1, '可以', 'kě yǐ', 'ke3 yi3', 'k''o³ i³', 'ㄎㄜˇ ㄧˇ', 'kee yii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (152, 104, 1, '課', 'kè', 'ke4', 'k''o⁴', 'ㄎㄜˋ', 'keh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (153, 105, 1, '口', 'kǒu', 'kou3', 'k''ou³', 'ㄎㄡˇ', 'koou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (154, 106, 1, '塊', 'kuài', 'kuai4', 'k''uai⁴', 'ㄎㄨㄞˋ', 'kuay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (155, 107, 1, '來', 'lái', 'lai2', 'lai²', 'ㄌㄞˊ', 'lai');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (156, 108, 1, '老師', 'lǎo shī', 'lao3 shi1', 'lao³ shih¹', 'ㄌㄠˇ ㄕ', 'lao shy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (157, 109, 1, '了', 'le', 'le5', 'le', 'ㄌㄜ˙', 'le');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (158, 109, 2, '了', 'liǎo', 'liao3', 'liao³', 'ㄌㄧㄠˇ', 'leau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (159, 109, 3, '瞭', 'liǎo', 'liao3', 'liao³', 'ㄌㄧㄠˇ', 'leau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (160, 109, 4, '瞭', 'liào', 'liao4', 'liao⁴', 'ㄌㄧㄠˋ', 'liaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (161, 110, 1, '冷', 'Lěng', 'Leng3', 'leng³', 'ㄌㄥˇ', 'leeng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (162, 110, 2, '冷', 'lěng', 'leng3', 'leng³', 'ㄌㄥˇ', 'leeng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (163, 111, 1, '裏', 'lǐ', 'li3', 'li³', 'ㄌㄧˇ', 'lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (164, 111, 2, '裡', 'lǐ', 'li3', 'li³', 'ㄌㄧˇ', 'lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (165, 111, 3, '里', 'Lǐ', 'Li3', 'li³', 'ㄌㄧˇ', 'lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (166, 111, 4, '里', 'lǐ', 'li3', 'li³', 'ㄌㄧˇ', 'lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (167, 112, 1, '兩', 'liǎng', 'liang3', 'liang³', 'ㄌㄧㄤˇ', 'leang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (168, 113, 1, '零', 'líng', 'ling2', 'ling²', 'ㄌㄧㄥˊ', 'ling');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (169, 114, 1, '六', 'liù', 'liu4', 'liu⁴', 'ㄌㄧㄡˋ', 'liow');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (170, 115, 1, '媽媽', 'mā ma', 'ma1 ma5', 'ma¹ ma', 'ㄇㄚ ㄇㄚ˙', 'mha ma');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (171, 116, 1, '嗎', 'má', 'ma2', 'ma²', 'ㄇㄚˊ', 'ma');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (172, 116, 2, '嗎', 'mǎ', 'ma3', 'ma³', 'ㄇㄚˇ', 'maa');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (173, 116, 3, '嗎', 'ma', 'ma5', 'ma', 'ㄇㄚ˙', 'ma');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (174, 117, 1, '買', 'mǎi', 'mai3', 'mai³', 'ㄇㄞˇ', 'mae');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (175, 118, 1, '賣', 'mài', 'mai4', 'mai⁴', 'ㄇㄞˋ', 'may');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (176, 119, 1, '忙', 'máng', 'mang2', 'mang²', 'ㄇㄤˊ', 'mang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (177, 120, 1, '貓', 'māo', 'mao1', 'mao¹', 'ㄇㄠ', 'mhau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (178, 121, 1, '沒關係', 'méi guān xi', 'mei2 guan1 xi5', 'mei² kuan¹ xi', 'ㄇㄟˊ ㄍㄨㄢ ㄒㄧ˙', 'mei guan xi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (179, 122, 1, '沒有', 'méi yǒu', 'mei2 you3', 'mei² yu³', 'ㄇㄟˊ ㄧㄡˇ', 'mei yeou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (180, 123, 1, '妹妹', 'mèi mei', 'mei4 mei5', 'mei⁴ mei', 'ㄇㄟˋ ㄇㄟ˙', 'mey mei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (181, 124, 1, '們', 'men', 'men5', 'men', 'ㄇㄣ˙', 'men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (182, 125, 1, '米飯', 'mǐ fàn', 'mi3 fan4', 'mi³ fan⁴', 'ㄇㄧˇ ㄈㄢˋ', 'mii fann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (183, 126, 1, '麵包', 'miàn bāo', 'mian4 bao1', 'mien⁴ pao¹', 'ㄇㄧㄢˋ ㄅㄠ', 'miann bau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (184, 127, 1, '麵條兒', 'miàn tiáo r', 'mian4 tiao2 r5', 'mien⁴ t''iao² r', 'ㄇㄧㄢˋ ㄊㄧㄠˊ ㄦ˙', 'miann tyau r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (185, 128, 1, '名字', 'míng zi', 'ming2 zi5', 'ming² zi', 'ㄇㄧㄥˊ ㄗ˙', 'ming zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (186, 129, 1, '明年', 'míng nián', 'ming2 nian2', 'ming² nien²', 'ㄇㄧㄥˊ ㄋㄧㄢˊ', 'ming nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (187, 130, 1, '明天', 'míng tiān', 'ming2 tian1', 'ming² t''ien¹', 'ㄇㄧㄥˊ ㄊㄧㄢ', 'ming tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (188, 131, 1, '哪', 'nǎ', 'na3', 'na³', 'ㄋㄚˇ', 'naa');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (189, 131, 2, '哪', 'na', 'na5', 'na', 'ㄋㄚ˙', 'na');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (190, 131, 3, '哪', 'né', 'ne2', 'ne²', 'ㄋㄜˊ', 'ne');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (191, 131, 4, '哪', 'něi', 'nei3', 'nei³', 'ㄋㄟˇ', 'neei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (192, 132, 1, '哪兒', 'nǎ r', 'na3 r5', 'na³ r', 'ㄋㄚˇ ㄦ˙', 'naa r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (193, 133, 1, '哪裏', 'nǎ lǐ', 'na3 li3', 'na³ li³', 'ㄋㄚˇ ㄌㄧˇ', 'naa lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (194, 133, 2, '哪裡', 'nǎ lǐ', 'na3 li3', 'na³ li³', 'ㄋㄚˇ ㄌㄧˇ', 'naa lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (195, 134, 1, '哪些', 'nǎ xiē', 'na3 xie1', 'na³ hsieh¹', 'ㄋㄚˇ ㄒㄧㄝ', 'naa shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (196, 135, 1, '那', 'Nā', 'Na1', 'na¹', 'ㄋㄚ', 'nha');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (197, 135, 2, '那', 'Nuó', 'Nuo2', 'no²', 'ㄋㄨㄛˊ', 'nuo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (198, 135, 3, '那', 'nǎ', 'na3', 'na³', 'ㄋㄚˇ', 'naa');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (199, 135, 4, '那', 'nà', 'na4', 'na⁴', 'ㄋㄚˋ', 'nah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (200, 135, 5, '那', 'nuó', 'nuo2', 'no²', 'ㄋㄨㄛˊ', 'nuo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (201, 136, 1, '那邊', 'nà bian', 'na4 bian5', 'na⁴ bian', 'ㄋㄚˋ ㄅㄧㄢ˙', 'nah bian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (202, 137, 1, '那兒', 'nà r', 'na4 r5', 'na⁴ r', 'ㄋㄚˋ ㄦ˙', 'nah r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (203, 138, 1, '那裏', 'nà li', 'na4 li5', 'na⁴ li', 'ㄋㄚˋ ㄌㄧ˙', 'nah li');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (204, 138, 2, '那裡', 'nà li', 'na4 li5', 'na⁴ li', 'ㄋㄚˋ ㄌㄧ˙', 'nah li');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (205, 139, 1, '那些', 'nà xiē', 'na4 xie1', 'na⁴ hsieh¹', 'ㄋㄚˋ ㄒㄧㄝ', 'nah shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (206, 140, 1, '男', 'nán', 'nan2', 'nan²', 'ㄋㄢˊ', 'nan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (207, 141, 1, '男朋友', 'nán péng you', 'nan2 peng2 you5', 'nan² p''eng² you', 'ㄋㄢˊ ㄆㄥˊ ㄧㄡ˙', 'nan perng you');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (208, 142, 1, '呢', 'ne', 'ne5', 'ne', 'ㄋㄜ˙', 'ne');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (209, 142, 2, '呢', 'ní', 'ni2', 'ni²', 'ㄋㄧˊ', 'ni');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (210, 143, 1, '能', 'Néng', 'Neng2', 'neng²', 'ㄋㄥˊ', 'neng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (211, 143, 2, '能', 'néng', 'neng2', 'neng²', 'ㄋㄥˊ', 'neng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (212, 144, 1, '你', 'nǐ', 'ni3', 'ni³', 'ㄋㄧˇ', 'nii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (213, 144, 2, '妳', 'nǐ', 'ni3', 'ni³', 'ㄋㄧˇ', 'nii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (214, 145, 1, '你們', 'nǐ men', 'ni3 men5', 'ni³ men', 'ㄋㄧˇ ㄇㄣ˙', 'nii men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (215, 146, 1, '年', 'Nián', 'Nian2', 'nien²', 'ㄋㄧㄢˊ', 'nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (216, 146, 2, '年', 'nián', 'nian2', 'nien²', 'ㄋㄧㄢˊ', 'nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (217, 146, 3, '秊', 'nián', 'nian2', 'nien²', 'ㄋㄧㄢˊ', 'nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (218, 147, 1, '您', 'nín', 'nin2', 'nin²', 'ㄋㄧㄣˊ', 'nin');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (219, 148, 1, '牛奶', 'niú nǎi', 'niu2 nai3', 'niu² nai³', 'ㄋㄧㄡˊ ㄋㄞˇ', 'niou nae');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (220, 149, 1, '女', 'nǚ', 'nü3', 'nu:3', 'ㄋㄩˇ', 'nu:3');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (221, 149, 2, '女', 'rǔ', 'ru3', 'ju³', 'ㄖㄨˇ', 'ruu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (222, 150, 1, '女兒', 'nǚ ér', 'nü3 er2', 'nu:3 erh²', 'ㄋㄩˇ ㄦˊ', 'nu:3 erl');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (223, 151, 1, '女朋友', 'nǚ péng you', 'nü3 peng2 you5', 'nu:3 p''eng² you', 'ㄋㄩˇ ㄆㄥˊ ㄧㄡ˙', 'nu:3 perng you');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (224, 152, 1, '女士', 'nǚ shì', 'nü3 shi4', 'nu:3 shih⁴', 'ㄋㄩˇ ㄕˋ', 'nu:3 shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (225, 153, 1, '朋友', 'péng you', 'peng2 you5', 'p''eng² you', 'ㄆㄥˊ ㄧㄡ˙', 'perng you');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (226, 154, 1, '漂亮', 'piào liang', 'piao4 liang5', 'p''iao⁴ liang', 'ㄆㄧㄠˋ ㄌㄧㄤ˙', 'piaw liang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (227, 155, 1, '蘋果', 'píng guǒ', 'ping2 guo3', 'p''ing² kuo³', 'ㄆㄧㄥˊ ㄍㄨㄛˇ', 'pyng guoo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (228, 156, 1, '七', 'qī', 'qi1', 'ch''i¹', 'ㄑㄧ', 'chi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (229, 157, 1, '起床', 'qǐ chuáng', 'qi3 chuang2', 'ch''i³ ch''uang²', 'ㄑㄧˇ ㄔㄨㄤˊ', 'chii chwang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (230, 158, 1, '千', 'qiān', 'qian1', 'ch''ien¹', 'ㄑㄧㄢ', 'chian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (231, 158, 2, '韆', 'qiān', 'qian1', 'ch''ien¹', 'ㄑㄧㄢ', 'chian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (232, 159, 1, '前', 'qián', 'qian2', 'ch''ien²', 'ㄑㄧㄢˊ', 'chyan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (233, 160, 1, '錢', 'Qián', 'Qian2', 'ch''ien²', 'ㄑㄧㄢˊ', 'chyan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (234, 160, 2, '錢', 'qián', 'qian2', 'ch''ien²', 'ㄑㄧㄢˊ', 'chyan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (235, 161, 1, '請', 'qǐng', 'qing3', 'ch''ing³', 'ㄑㄧㄥˇ', 'chiing');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (236, 162, 1, '請問', 'qǐng wèn', 'qing3 wen4', 'ch''ing³ wen⁴', 'ㄑㄧㄥˇ ㄨㄣˋ', 'chiing wenn');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (237, 163, 1, '去', 'qù', 'qu4', 'ch''ü⁴', 'ㄑㄩˋ', 'chiuh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (238, 164, 1, '去年', 'qù nián', 'qu4 nian2', 'ch''ü⁴ nien²', 'ㄑㄩˋ ㄋㄧㄢˊ', 'chiuh nian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (239, 165, 1, '熱', 'rè', 're4', 'je⁴', 'ㄖㄜˋ', 'reh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (240, 166, 1, '人', 'rén', 'ren2', 'jen²', 'ㄖㄣˊ', 'ren');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (241, 167, 1, '認識', 'rèn shi', 'ren4 shi5', 'jen⁴ shi', 'ㄖㄣˋ ㄕ˙', 'renn shi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (242, 168, 1, '日', 'Rì', 'Ri4', 'jih⁴', 'ㄖˋ', 'ryh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (243, 168, 2, '日', 'rì', 'ri4', 'jih⁴', 'ㄖˋ', 'ryh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (244, 169, 1, '三', 'Sān', 'San1', 'san¹', 'ㄙㄢ', 'san');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (245, 169, 2, '三', 'sān', 'san1', 'san¹', 'ㄙㄢ', 'san');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (246, 170, 1, '商店', 'shāng diàn', 'shang1 dian4', 'shang¹ tien⁴', 'ㄕㄤ ㄉㄧㄢˋ', 'shang diann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (247, 171, 1, '上', 'shǎng', 'shang3', 'shang³', 'ㄕㄤˇ', 'shaang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (248, 171, 2, '上', 'shàng', 'shang4', 'shang⁴', 'ㄕㄤˋ', 'shanq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (249, 172, 1, '上班', 'shàng bān', 'shang4 ban1', 'shang⁴ pan¹', 'ㄕㄤˋ ㄅㄢ', 'shanq ban');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (250, 173, 1, '上課', 'shàng kè', 'shang4 ke4', 'shang⁴ k''o⁴', 'ㄕㄤˋ ㄎㄜˋ', 'shanq keh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (251, 174, 1, '上午', 'shàng wǔ', 'shang4 wu3', 'shang⁴ wu³', 'ㄕㄤˋ ㄨˇ', 'shanq wuu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (252, 175, 1, '上學', 'shàng xué', 'shang4 xue2', 'shang⁴ hsüeh²', 'ㄕㄤˋ ㄒㄩㄝˊ', 'shanq shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (253, 176, 1, '少', 'shǎo', 'shao3', 'shao³', 'ㄕㄠˇ', 'shao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (254, 176, 2, '少', 'shào', 'shao4', 'shao⁴', 'ㄕㄠˋ', 'shaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (255, 177, 1, '什麼', 'shén me', 'shen2 me5', 'shen² me', 'ㄕㄣˊ ㄇㄜ˙', 'shern me');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (256, 178, 1, '生病', 'shēng bìng', 'sheng1 bing4', 'sheng¹ ping⁴', 'ㄕㄥ ㄅㄧㄥˋ', 'sheng binq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (257, 179, 1, '十', 'shí', 'shi2', 'shih²', 'ㄕˊ', 'shyr');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (258, 180, 1, '時候', 'shí hou', 'shi2 hou5', 'shih² hou', 'ㄕˊ ㄏㄡ˙', 'shyr hou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (259, 181, 1, '時間', 'shí jiān', 'shi2 jian1', 'shih² chien¹', 'ㄕˊ ㄐㄧㄢ', 'shyr jian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (260, 182, 1, '事', 'shì', 'shi4', 'shih⁴', 'ㄕˋ', 'shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (261, 183, 1, '是', 'shì', 'shi4', 'shih⁴', 'ㄕˋ', 'shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (262, 183, 2, '昰', 'shì', 'shi4', 'shih⁴', 'ㄕˋ', 'shyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (263, 184, 1, '手機', 'shǒu jī', 'shou3 ji1', 'shou³ chi¹', 'ㄕㄡˇ ㄐㄧ', 'shoou ji');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (264, 185, 1, '書', 'Shū', 'Shu1', 'shu¹', 'ㄕㄨ', 'shu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (265, 185, 2, '書', 'shū', 'shu1', 'shu¹', 'ㄕㄨ', 'shu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (266, 186, 1, '書店', 'shū diàn', 'shu1 dian4', 'shu¹ tien⁴', 'ㄕㄨ ㄉㄧㄢˋ', 'shu diann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (267, 187, 1, '誰', 'shéi', 'shei2', 'shei²', 'ㄕㄟˊ', 'sheir');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (268, 188, 1, '水', 'Shuǐ', 'Shui3', 'shui³', 'ㄕㄨㄟˇ', 'shoei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (269, 188, 2, '水', 'shuǐ', 'shui3', 'shui³', 'ㄕㄨㄟˇ', 'shoei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (270, 189, 1, '水果', 'shuǐ guǒ', 'shui3 guo3', 'shui³ kuo³', 'ㄕㄨㄟˇ ㄍㄨㄛˇ', 'shoei guoo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (271, 190, 1, '睡', 'shuì', 'shui4', 'shui⁴', 'ㄕㄨㄟˋ', 'shuey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (272, 191, 1, '睡覺', 'shuì jiào', 'shui4 jiao4', 'shui⁴ chiao⁴', 'ㄕㄨㄟˋ ㄐㄧㄠˋ', 'shuey jiaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (273, 192, 1, '說', 'shuì', 'shui4', 'shui⁴', 'ㄕㄨㄟˋ', 'shuey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (274, 192, 2, '說', 'shuō', 'shuo1', 'shuo¹', 'ㄕㄨㄛ', 'shuo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (275, 192, 3, '説', 'shuō', 'shuo1', 'shuo¹', 'ㄕㄨㄛ', 'shuo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (276, 193, 1, '說話', 'shuō huà', 'shuo1 hua4', 'shuo¹ hua⁴', 'ㄕㄨㄛ ㄏㄨㄚˋ', 'shuo huah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (277, 194, 1, '四', 'sì', 'si4', 'ssu⁴', 'ㄙˋ', 'syh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (278, 195, 1, '嵗', 'suì', 'sui4', 'sui⁴', 'ㄙㄨㄟˋ', 'suey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (279, 195, 2, '歲', 'suì', 'sui4', 'sui⁴', 'ㄙㄨㄟˋ', 'suey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (280, 196, 1, '他', 'tā', 'ta1', 't''a¹', 'ㄊㄚ', 'ta');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (281, 197, 1, '他們', 'tā men', 'ta1 men5', 't''a¹ men', 'ㄊㄚ ㄇㄣ˙', 'ta men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (282, 198, 1, '它', 'tā', 'ta1', 't''a¹', 'ㄊㄚ', 'ta');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (283, 199, 1, '它們', 'tā men', 'ta1 men5', 't''a¹ men', 'ㄊㄚ ㄇㄣ˙', 'ta men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (284, 200, 1, '她', 'tā', 'ta1', 't''a¹', 'ㄊㄚ', 'ta');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (285, 201, 1, '她們', 'tā men', 'ta1 men5', 't''a¹ men', 'ㄊㄚ ㄇㄣ˙', 'ta men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (286, 202, 1, '太', 'tài', 'tai4', 't''ai⁴', 'ㄊㄞˋ', 'tay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (287, 203, 1, '天', 'tiān', 'tian1', 't''ien¹', 'ㄊㄧㄢ', 'tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (288, 204, 1, '天氣', 'tiān qì', 'tian1 qi4', 't''ien¹ ch''i⁴', 'ㄊㄧㄢ ㄑㄧˋ', 'tian chih');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (289, 205, 1, '听', 'yǐn', 'yin3', 'yin³', 'ㄧㄣˇ', 'yiin');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (290, 205, 2, '聽', 'tīng', 'ting1', 't''ing¹', 'ㄊㄧㄥ', 'ting');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (291, 206, 1, '聽見', 'tīng jiàn', 'ting1 jian4', 't''ing¹ chien⁴', 'ㄊㄧㄥ ㄐㄧㄢˋ', 'ting jiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (292, 207, 1, '同學', 'tóng xué', 'tong2 xue2', 't''ung² hsüeh²', 'ㄊㄨㄥˊ ㄒㄩㄝˊ', 'torng shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (293, 208, 1, '外', 'wài', 'wai4', 'wai⁴', 'ㄨㄞˋ', 'way');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (294, 209, 1, '外邊', 'wài bian', 'wai4 bian5', 'wai⁴ bian', 'ㄨㄞˋ ㄅㄧㄢ˙', 'way bian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (295, 210, 1, '玩', 'wán', 'wan2', 'wan²', 'ㄨㄢˊ', 'wan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (296, 210, 2, '翫', 'wán', 'wan2', 'wan²', 'ㄨㄢˊ', 'wan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (297, 211, 1, '晚', 'wǎn', 'wan3', 'wan³', 'ㄨㄢˇ', 'woan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (298, 212, 1, '晚飯', 'wǎn fàn', 'wan3 fan4', 'wan³ fan⁴', 'ㄨㄢˇ ㄈㄢˋ', 'woan fann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (299, 213, 1, '晚上', 'wǎn shang', 'wan3 shang5', 'wan³ shang', 'ㄨㄢˇ ㄕㄤ˙', 'woan shang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (300, 214, 1, '喂', 'wéi', 'wei2', 'wei²', 'ㄨㄟˊ', 'wei');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (301, 214, 2, '喂', 'wèi', 'wei4', 'wei⁴', 'ㄨㄟˋ', 'wey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (302, 214, 3, '餧', 'wèi', 'wei4', 'wei⁴', 'ㄨㄟˋ', 'wey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (303, 214, 4, '餵', 'wèi', 'wei4', 'wei⁴', 'ㄨㄟˋ', 'wey');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (304, 215, 1, '問', 'wèn', 'wen4', 'wen⁴', 'ㄨㄣˋ', 'wenn');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (305, 216, 1, '問題', 'wèn tí', 'wen4 ti2', 'wen⁴ t''i²', 'ㄨㄣˋ ㄊㄧˊ', 'wenn tyi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (306, 217, 1, '我', 'wǒ', 'wo3', 'wo³', 'ㄨㄛˇ', 'woo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (307, 218, 1, '我們', 'wǒ men', 'wo3 men5', 'wo³ men', 'ㄨㄛˇ ㄇㄣ˙', 'woo men');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (308, 219, 1, '五', 'wǔ', 'wu3', 'wu³', 'ㄨˇ', 'wuu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (309, 220, 1, '午飯', 'wǔ fàn', 'wu3 fan4', 'wu³ fan⁴', 'ㄨˇ ㄈㄢˋ', 'wuu fann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (310, 221, 1, '喜歡', 'xǐ huan', 'xi3 huan5', 'hsi³ huan', 'ㄒㄧˇ ㄏㄨㄢ˙', 'shii huan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (311, 222, 1, '下', 'xià', 'xia4', 'hsia⁴', 'ㄒㄧㄚˋ', 'shiah');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (312, 223, 1, '下班', 'xià bān', 'xia4 ban1', 'hsia⁴ pan¹', 'ㄒㄧㄚˋ ㄅㄢ', 'shiah ban');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (313, 224, 1, '下課', 'xià kè', 'xia4 ke4', 'hsia⁴ k''o⁴', 'ㄒㄧㄚˋ ㄎㄜˋ', 'shiah keh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (314, 225, 1, '下午', 'xià wǔ', 'xia4 wu3', 'hsia⁴ wu³', 'ㄒㄧㄚˋ ㄨˇ', 'shiah wuu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (315, 226, 1, '下雨', 'xià yǔ', 'xia4 yu3', 'hsia⁴ yü³', 'ㄒㄧㄚˋ ㄩˇ', 'shiah yeu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (316, 227, 1, '先生', 'xiān sheng', 'xian1 sheng5', 'hsien¹ sheng', 'ㄒㄧㄢ ㄕㄥ˙', 'shian sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (317, 228, 1, '現在', 'xiàn zài', 'xian4 zai4', 'hsien⁴ tsai⁴', 'ㄒㄧㄢˋ ㄗㄞˋ', 'shiann tzay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (318, 229, 1, '想', 'xiǎng', 'xiang3', 'hsiang³', 'ㄒㄧㄤˇ', 'sheang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (319, 230, 1, '小', 'xiǎo', 'xiao3', 'hsiao³', 'ㄒㄧㄠˇ', 'sheau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (320, 231, 1, '小朋友', 'xiǎo péng yǒu', 'xiao3 peng2 you3', 'hsiao³ p''eng² yu³', 'ㄒㄧㄠˇ ㄆㄥˊ ㄧㄡˇ', 'sheau perng yeou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (321, 232, 1, '小時', 'xiǎo shí', 'xiao3 shi2', 'hsiao³ shih²', 'ㄒㄧㄠˇ ㄕˊ', 'sheau shyr');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (322, 233, 1, '小學', 'xiǎo xué', 'xiao3 xue2', 'hsiao³ hsüeh²', 'ㄒㄧㄠˇ ㄒㄩㄝˊ', 'sheau shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (323, 234, 1, '小學生', 'xiǎo xué shēng', 'xiao3 xue2 sheng1', 'hsiao³ hsüeh² sheng¹', 'ㄒㄧㄠˇ ㄒㄩㄝˊ ㄕㄥ', 'sheau shyue sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (324, 235, 1, '些', 'xiē', 'xie1', 'hsieh¹', 'ㄒㄧㄝ', 'shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (325, 236, 1, '寫', 'xiě', 'xie3', 'hsieh³', 'ㄒㄧㄝˇ', 'shiee');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (326, 237, 1, '謝謝', 'xiè xie', 'xie4 xie5', 'hsieh⁴ xie', 'ㄒㄧㄝˋ ㄒㄧㄝ˙', 'shieh xie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (327, 238, 1, '新', 'Xīn', 'Xin1', 'hsin¹', 'ㄒㄧㄣ', 'shin');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (328, 238, 2, '新', 'xīn', 'xin1', 'hsin¹', 'ㄒㄧㄣ', 'shin');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (329, 239, 1, '星期', 'xīng qī', 'xing1 qi1', 'hsing¹ ch''i¹', 'ㄒㄧㄥ ㄑㄧ', 'shing chi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (330, 240, 1, '星期日', 'Xīng qī rì', 'Xing1 qi1 ri4', 'hsing¹ ch''i¹ jih⁴', 'ㄒㄧㄥ ㄑㄧ ㄖˋ', 'shing chi ryh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (331, 241, 1, '星期天', 'Xīng qī tiān', 'Xing1 qi1 tian1', 'hsing¹ ch''i¹ t''ien¹', 'ㄒㄧㄥ ㄑㄧ ㄊㄧㄢ', 'shing chi tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (332, 242, 1, '休息', 'xiū xi', 'xiu1 xi5', 'hsiu¹ xi', 'ㄒㄧㄡ ㄒㄧ˙', 'shiou xi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (333, 243, 1, '學', 'xué', 'xue2', 'hsüeh²', 'ㄒㄩㄝˊ', 'shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (334, 244, 1, '學生', 'xué sheng', 'xue2 sheng5', 'hsüeh² sheng', 'ㄒㄩㄝˊ ㄕㄥ˙', 'shyue sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (335, 245, 1, '學習', 'xué xí', 'xue2 xi2', 'hsüeh² hsi²', 'ㄒㄩㄝˊ ㄒㄧˊ', 'shyue shyi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (336, 246, 1, '學校', 'xué xiào', 'xue2 xiao4', 'hsüeh² hsiao⁴', 'ㄒㄩㄝˊ ㄒㄧㄠˋ', 'shyue shiaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (337, 247, 1, '雪', 'Xuě', 'Xue3', 'hsüeh³', 'ㄒㄩㄝˇ', 'sheue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (338, 247, 2, '雪', 'xuě', 'xue3', 'hsüeh³', 'ㄒㄩㄝˇ', 'sheue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (339, 248, 1, '要', 'yāo', 'yao1', 'yao¹', 'ㄧㄠ', 'iau');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (340, 248, 2, '要', 'yào', 'yao4', 'yao⁴', 'ㄧㄠˋ', 'yaw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (341, 249, 1, '也', 'Yě', 'Ye3', 'yeh³', 'ㄧㄝˇ', 'yee');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (342, 249, 2, '也', 'yě', 'ye3', 'yeh³', 'ㄧㄝˇ', 'yee');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (343, 250, 1, '一', 'yī', 'yi1', 'i¹', 'ㄧ', 'i');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (344, 251, 1, '一半', 'yī bàn', 'yi1 ban4', 'i¹ pan⁴', 'ㄧ ㄅㄢˋ', 'i bann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (345, 252, 1, '一點兒', 'yī diǎn r', 'yi1 dian3 r5', 'i¹ tien³ r', 'ㄧ ㄉㄧㄢˇ ㄦ˙', 'i dean r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (346, 253, 1, '一些', 'yī xiē', 'yi1 xie1', 'i¹ hsieh¹', 'ㄧ ㄒㄧㄝ', 'i shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (347, 254, 1, '衣服', 'yī fu', 'yi1 fu5', 'i¹ fu', 'ㄧ ㄈㄨ˙', 'i fu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (348, 255, 1, '醫生', 'yī shēng', 'yi1 sheng1', 'i¹ sheng¹', 'ㄧ ㄕㄥ', 'i sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (349, 256, 1, '醫院', 'yī yuàn', 'yi1 yuan4', 'i¹ yüan⁴', 'ㄧ ㄩㄢˋ', 'i yuann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (350, 257, 1, '椅子', 'yǐ zi', 'yi3 zi5', 'i³ zi', 'ㄧˇ ㄗ˙', 'yii zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (351, 258, 1, '有', 'yǒu', 'you3', 'yu³', 'ㄧㄡˇ', 'yeou');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (352, 259, 1, '有的', 'yǒu de', 'you3 de5', 'yu³ de', 'ㄧㄡˇ ㄉㄜ˙', 'yeou de');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (353, 260, 1, '有點兒', 'yǒu diǎn r', 'you3 dian3 r5', 'yu³ tien³ r', 'ㄧㄡˇ ㄉㄧㄢˇ ㄦ˙', 'yeou dean r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (354, 261, 1, '有些', 'yǒu xiē', 'you3 xie1', 'yu³ hsieh¹', 'ㄧㄡˇ ㄒㄧㄝ', 'yeou shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (355, 262, 1, '雨', 'yǔ', 'yu3', 'yü³', 'ㄩˇ', 'yeu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (356, 262, 2, '雨', 'yù', 'yu4', 'yü⁴', 'ㄩˋ', 'yuh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (357, 263, 1, '元', 'Yuán', 'Yuan2', 'yüan²', 'ㄩㄢˊ', 'yuan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (358, 263, 2, '元', 'yuán', 'yuan2', 'yüan²', 'ㄩㄢˊ', 'yuan');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (359, 264, 1, '月', 'yuè', 'yue4', 'yüeh⁴', 'ㄩㄝˋ', 'yueh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (360, 265, 1, '再', 'zài', 'zai4', 'tsai⁴', 'ㄗㄞˋ', 'tzay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (361, 266, 1, '再見', 'zài jiàn', 'zai4 jian4', 'tsai⁴ chien⁴', 'ㄗㄞˋ ㄐㄧㄢˋ', 'tzay jiann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (362, 267, 1, '在', 'zài', 'zai4', 'tsai⁴', 'ㄗㄞˋ', 'tzay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (363, 268, 1, '早', 'zǎo', 'zao3', 'tsao³', 'ㄗㄠˇ', 'tzao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (364, 269, 1, '早飯', 'zǎo fàn', 'zao3 fan4', 'tsao³ fan⁴', 'ㄗㄠˇ ㄈㄢˋ', 'tzao fann');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (365, 270, 1, '早上', 'zǎo shang', 'zao3 shang5', 'tsao³ shang', 'ㄗㄠˇ ㄕㄤ˙', 'tzao shang');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (366, 271, 1, '怎麼', 'zěn me', 'zen3 me5', 'tsen³ me', 'ㄗㄣˇ ㄇㄜ˙', 'tzeen me');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (367, 271, 2, '怎麽', 'zěn me', 'zen3 me5', 'tsen³ me', 'ㄗㄣˇ ㄇㄜ˙', 'tzeen me');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (368, 272, 1, '怎麼樣', 'zěn me yàng', 'zen3 me5 yang4', 'tsen³ me yang⁴', 'ㄗㄣˇ ㄇㄜ˙ ㄧㄤˋ', 'tzeen me yanq');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (369, 273, 1, '找', 'zhǎo', 'zhao3', 'chao³', 'ㄓㄠˇ', 'jao');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (370, 274, 1, '這', 'zhè', 'zhe4', 'che⁴', 'ㄓㄜˋ', 'jeh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (371, 275, 1, '這邊', 'zhè biān', 'zhe4 bian1', 'che⁴ pien¹', 'ㄓㄜˋ ㄅㄧㄢ', 'jeh bian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (372, 276, 1, '這兒', 'zhè r', 'zhe4 r5', 'che⁴ r', 'ㄓㄜˋ ㄦ˙', 'jeh r');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (373, 277, 1, '這裏', 'zhè lǐ', 'zhe4 li3', 'che⁴ li³', 'ㄓㄜˋ ㄌㄧˇ', 'jeh lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (374, 277, 2, '這裡', 'zhè lǐ', 'zhe4 li3', 'che⁴ li³', 'ㄓㄜˋ ㄌㄧˇ', 'jeh lii');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (375, 278, 1, '這些', 'zhè xiē', 'zhe4 xie1', 'che⁴ hsieh¹', 'ㄓㄜˋ ㄒㄧㄝ', 'jeh shie');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (376, 279, 1, '真', 'zhēn', 'zhen1', 'chen¹', 'ㄓㄣ', 'jen');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (377, 280, 1, '正在', 'zhèng zài', 'zheng4 zai4', 'cheng⁴ tsai⁴', 'ㄓㄥˋ ㄗㄞˋ', 'jenq tzay');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (378, 281, 1, '知道', 'zhī dào', 'zhi1 dao4', 'chih¹ tao⁴', 'ㄓ ㄉㄠˋ', 'jy daw');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (379, 282, 1, '只', 'zhǐ', 'zhi3', 'chih³', 'ㄓˇ', 'jyy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (380, 282, 2, '祇', 'zhǐ', 'zhi3', 'chih³', 'ㄓˇ', 'jyy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (381, 282, 3, '秖', 'zhī', 'zhi1', 'chih¹', 'ㄓ', 'jy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (382, 282, 4, '衹', 'zhǐ', 'zhi3', 'chih³', 'ㄓˇ', 'jyy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (383, 282, 5, '隻', 'zhī', 'zhi1', 'chih¹', 'ㄓ', 'jy');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (384, 283, 1, '中國', 'Zhōng guó', 'Zhong1 guo2', 'chung¹ kuo²', 'ㄓㄨㄥ ㄍㄨㄛˊ', 'jong gwo');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (385, 284, 1, '中文', 'Zhōng wén', 'Zhong1 wen2', 'chung¹ wen²', 'ㄓㄨㄥ ㄨㄣˊ', 'jong wen');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (386, 285, 1, '中午', 'zhōng wǔ', 'zhong1 wu3', 'chung¹ wu³', 'ㄓㄨㄥ ㄨˇ', 'jong wuu');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (387, 286, 1, '中學', 'zhōng xué', 'zhong1 xue2', 'chung¹ hsüeh²', 'ㄓㄨㄥ ㄒㄩㄝˊ', 'jong shyue');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (388, 287, 1, '中學生', 'zhōng xué shēng', 'zhong1 xue2 sheng1', 'chung¹ hsüeh² sheng¹', 'ㄓㄨㄥ ㄒㄩㄝˊ ㄕㄥ', 'jong shyue sheng');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (389, 288, 1, '住', 'zhù', 'zhu4', 'chu⁴', 'ㄓㄨˋ', 'juh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (390, 289, 1, '桌子', 'zhuō zi', 'zhuo1 zi5', 'cho¹ zi', 'ㄓㄨㄛ ㄗ˙', 'juo zi');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (391, 290, 1, '字', 'zì', 'zi4', 'tzu⁴', 'ㄗˋ', 'tzyh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (392, 291, 1, '昨天', 'zuó tiān', 'zuo2 tian1', 'tso² t''ien¹', 'ㄗㄨㄛˊ ㄊㄧㄢ', 'tzwo tian');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (393, 292, 1, '坐', 'Zuò', 'Zuo4', 'tso⁴', 'ㄗㄨㄛˋ', 'tzuoh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (394, 292, 2, '坐', 'zuò', 'zuo4', 'tso⁴', 'ㄗㄨㄛˋ', 'tzuoh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (395, 293, 1, '做', 'zuò', 'zuo4', 'tso⁴', 'ㄗㄨㄛˋ', 'tzuoh');

INSERT INTO vocabulary_reading (id, vocabulary_id, position, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh) VALUES (396, 294, 1, '做飯', 'zuò fàn', 'zuo4 fan4', 'tso⁴ fan⁴', 'ㄗㄨㄛˋ ㄈㄢˋ', 'tzuoh fann');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (1, 1, 'to love; to be fond of; to like');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (1, 2, 'affection');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (1, 3, 'to be inclined (to do sth); to tend to (happen)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (2, 1, 'eight; 8');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (3, 1, '(coll.) father; dad');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (4, 1, 'bar (loanword) (serving drinks, or providing Internet access etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (4, 2, 'to puff (on a pipe etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (4, 3, '(onom.) bang');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (4, 4, 'abbr. for 贴吧');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (5, 1, '(modal particle indicating suggestion or surmise)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (5, 2, '...right?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (5, 3, '...OK?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (5, 4, '...I presume.');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (6, 1, '(onom.) smack!');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (7, 1, 'daytime');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (7, 2, 'during the day');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (7, 3, 'day');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (8, 1, 'surname Bai');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (9, 1, 'hundred');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (9, 2, 'numerous');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (9, 3, 'all kinds of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (10, 1, 'half');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (10, 2, 'semi-');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (10, 3, 'incomplete');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (10, 4, '(after a number) and a half');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (11, 1, 'bao (steamed stuffed bun)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (12, 1, 'cup');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (12, 2, 'glass');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 1, 'root');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 2, 'stem');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 3, 'origin');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 4, 'source');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 5, 'this');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 6, 'the current');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 7, 'original');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 8, 'inherent');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 9, 'originally');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (13, 10, 'classifier for books, periodicals, files etc');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 1, 'side');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 2, 'edge');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 3, 'margin');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 4, 'border');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 5, 'boundary');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (14, 6, 'simultaneously');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (15, 1, 'suffix of a noun of locality');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (16, 1, 'convenient');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (17, 1, 'cheap');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (17, 2, 'inexpensive');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (17, 3, 'small advantages');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (17, 4, 'to let sb off lightly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (18, 1, 'illness');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (18, 2, 'disease');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (18, 3, 'to fall ill');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (18, 4, 'defect');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (19, 1, 'no; not so');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (19, 2, '(bound form) not; un-');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (20, 1, 'you''re welcome');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (20, 2, 'don''t mention it');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (20, 3, 'impolite');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (20, 4, 'rude');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (20, 5, 'blunt');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (21, 1, 'don''t!');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (21, 2, 'must not');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 1, 'dish (type of food)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 2, 'vegetable');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 3, 'cuisine');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 4, '(coll.) (one''s) type');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 5, '(of one''s skills etc) weak');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (22, 6, 'poor');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (23, 1, 'tea');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (23, 2, 'tea plant');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (24, 1, 'to sing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (24, 2, 'to call loudly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (24, 3, 'to chant');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (25, 1, 'supermarket (abbr. for 超级市场)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (26, 1, 'surname Che');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (27, 1, 'car');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (27, 2, 'vehicle');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (27, 3, 'machine');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (27, 4, 'to shape with a lathe');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (27, 5, 'Kangxi radical 159');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (28, 1, 'war chariot (archaic)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (28, 2, 'rook (in Chinese chess)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (28, 3, 'rook (in chess)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (29, 1, 'to eat; to consume');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (29, 2, 'to eat at (a cafeteria etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (29, 3, 'to eradicate; to destroy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (29, 4, 'to absorb');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (29, 5, 'to suffer (shock, injury, defeat etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (30, 1, 'variant of 吃');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (31, 1, 'taxi');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (31, 2, '(Tw) rental car');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 1, 'to wear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 2, 'to put on');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 3, 'to dress');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 4, 'to bore through');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 5, 'to pierce');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 6, 'to perforate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 7, 'to penetrate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 8, 'to pass through');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (32, 9, 'to thread');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (33, 1, 'to make a telephone call');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 1, 'big; large; great');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 2, 'older (than another person)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 3, 'eldest (as in 姐)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 4, 'greatly; freely; fully');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 5, '(dialect) father');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (34, 6, '(dialect) uncle (father''s brother)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (35, 1, 'see 夫');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (36, 1, 'everyone');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (36, 2, 'influential family');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (36, 3, 'great expert');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (37, 1, 'the Great Learning, one of the Four Books 四书 in Confucianism');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (38, 1, 'university');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (38, 2, 'college');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (39, 1, 'university student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (39, 2, 'college student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (40, 1, 'to reach; to arrive');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (40, 2, 'to leave for; to go to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (40, 3, 'to (a place); until (a time); up to (a point)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (40, 4, '(verb complement indicating arriving at a place or reaching a point)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (40, 5, 'considerate; thoughtful; thorough');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (41, 1, 'of; ~''s (possessive particle)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (41, 2, '(used after an attribute)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (41, 3, '(used to form a nominal expression)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (41, 4, '(used at the end of a declarative sentence for emphasis)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (41, 5, 'also pr. [dì] or [di] in poetry and songs');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (42, 1, 'a taxi; a cab (abbr. for 士)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (43, 1, 'really and truly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (44, 1, '(bound form) bull''s-eye; target');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (45, 1, 'younger brother');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (46, 1, '(prefix indicating ordinal number, as in 六 "sixth")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (46, 2, '(literary) grades in which successful candidates in the imperial examinations were placed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (46, 3, '(old) residence of a high official');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (46, 4, '(literary) but; however');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (46, 5, '(literary) only; just');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 1, 'point');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 2, 'dot');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 3, 'drop');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 4, 'speck');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 5, 'o''clock');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 6, 'point (in space or time)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 7, 'to draw a dot');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 8, 'to check on a list');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 9, 'to choose');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 10, 'to order (food in a restaurant)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 11, 'to touch briefly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 12, 'to hint');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 13, 'to light');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 14, 'to ignite');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 15, 'to pour a liquid drop by drop');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 16, '(old) one fifth of a two-hour watch 更');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 17, 'dot stroke in Chinese characters');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (47, 18, 'classifier for items');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (48, 1, 'telephone');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (48, 2, 'phone call');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (48, 3, 'phone number');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (49, 1, 'computer');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (50, 1, 'television; TV');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (51, 1, 'movie; film');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (52, 1, 'cinema; movie theater');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (53, 1, 'inn; old-style hotel');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (53, 2, '(bound form) shop; store');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (54, 1, 'east and west');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (55, 1, 'thing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (55, 2, 'stuff');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (55, 3, 'person');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (56, 1, 'surname Du');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (57, 1, 'all; both; entirely');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (57, 2, '(used for emphasis) even');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (57, 3, 'already');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (57, 4, '(not) at all');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (58, 1, 'capital city');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (58, 2, 'metropolis');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (59, 1, 'comma');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (59, 2, 'phrase marked by pause');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (60, 1, 'to read out; to read aloud');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (60, 2, 'to read');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (60, 3, 'to attend (school); to study (a subject in school)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (60, 4, 'to pronounce');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (61, 1, 'to read a book');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (61, 2, 'to study');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (61, 3, 'to attend school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 1, 'right; correct');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 2, 'towards; at; for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 3, 'concerning; regarding');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 4, 'to treat (sb a certain way)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 5, 'to face');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 6, '(bound form) opposite; facing; matching');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 7, 'to match together; to adjust');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 8, 'to fit; to suit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 9, 'to answer; to reply');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 10, 'to add; to pour in (a fluid)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 11, 'to check; to compare');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (62, 12, 'classifier: couple; pair');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (63, 1, 'I''m sorry; excuse me; I beg your pardon');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (63, 2, 'to let (sb) down; to disappoint');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (64, 1, 'many; much');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (64, 2, 'too many; in excess');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (64, 3, '(after a numeral) ... odd');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (64, 4, 'how (to what extent) (Taiwan pr. [duó])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (64, 5, '(bound form) multi-; poly-');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (65, 1, 'number');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (65, 2, 'amount');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (65, 3, 'somewhat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (66, 1, 'how much?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (66, 2, 'how many?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (66, 3, '(phone number, student ID etc) what number?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (67, 1, 'son');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (68, 1, 'two');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (68, 2, '2');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (68, 3, '(Beijing dialect) stupid');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (69, 1, 'cooked rice');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (69, 2, 'meal');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (69, 3, '(loanword) fan');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (69, 4, 'devotee');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (70, 1, 'restaurant');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (70, 2, 'hotel');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (71, 1, 'room');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (72, 1, 'airplane');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (73, 1, 'very; really');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (73, 2, 'unusual; extraordinary');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 1, 'to divide; to separate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 2, 'to distribute; to allocate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 3, 'to distinguish (good and bad)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 4, '(bound form) branch of (an organization); sub- (as in 局)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 5, 'fraction');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 6, 'one tenth (of certain units)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 7, 'unit of length equivalent to 0.33 cm');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 8, 'minute (unit of time)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 9, 'minute (angular measurement unit)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 10, 'a point (in sports or games)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (74, 11, '0.01 yuan (unit of money)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (75, 1, 'part');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (75, 2, 'share');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (75, 3, 'ingredient');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (75, 4, 'component');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (76, 1, 'minute');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (77, 1, 'happy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (77, 2, 'glad');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (77, 3, 'willing (to do sth)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (77, 4, 'in a cheerful mood');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (78, 1, 'older brother');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (79, 1, 'song');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (79, 2, 'to sing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (80, 1, 'variant of 歌');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (81, 1, 'used in 自个儿');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (82, 1, '(classifier used before a noun that has no specific classifier)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (82, 2, '(bound form) individual');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (83, 1, 'variant of 个');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 1, 'to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 2, 'for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 3, 'for the benefit of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 4, 'to give');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 5, 'to allow');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 6, 'to do sth (for sb)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 7, '(grammatical equivalent of 被)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 8, '(grammatical equivalent of 把)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (84, 9, '(sentence intensifier)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (85, 1, 'to supply');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (85, 2, 'to provide');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (86, 1, 'to work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (86, 2, '(of a machine) to operate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (86, 3, 'job');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (86, 4, 'work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (86, 5, 'task');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (87, 1, 'company; firm; corporation');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (88, 1, 'dog');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (89, 1, 'expensive');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (89, 2, 'noble');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (89, 3, 'precious');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (89, 4, '(honorific) your');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (90, 1, 'surname Guo');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (91, 1, 'country; nation; state');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (91, 2, '(bound form) national');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (92, 1, 'surname Huan');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 1, 'still');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 2, 'still in progress');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 3, 'still more');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 4, 'yet');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 5, 'even more');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 6, 'in addition');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 7, 'fairly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 8, 'passably (good)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 9, 'as early as');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 10, 'even');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 11, 'also');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (93, 12, 'else');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (94, 1, 'to pay back');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (94, 2, 'to return');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (95, 1, 'child');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (96, 1, 'Chinese language');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (97, 1, 'Chinese character');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (97, 2, 'Japanese: kanji');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (97, 3, 'Korean: hanja');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (97, 4, 'Vietnamese: hán tự');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 1, 'good');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 2, 'appropriate; proper');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 3, 'all right!');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 4, '(before a verb) easy to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 5, '(before a verb) good to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 6, '(before an adjective for exclamatory effect) so');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 7, '(verb complement indicating completion)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 8, '(of two people) close; on intimate terms');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (98, 9, '(after a personal pronoun) hello');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (99, 1, 'to be fond of; to have a tendency to; to be prone to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (100, 1, 'tasty');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (100, 2, 'delicious');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (101, 1, 'to be fond of eating');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (101, 2, 'to be gluttonous');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (102, 1, 'good-looking');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (102, 2, 'nice-looking');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (102, 3, 'good (of a movie, book, TV show etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (102, 4, 'embarrassed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (102, 5, 'humiliated');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (103, 1, 'pleasant to hear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (104, 1, 'erhua variant of 好玩');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (104, 2, 'amusing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (104, 3, 'fun');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (104, 4, 'interesting');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (105, 1, 'roar');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (105, 2, 'cry');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 1, 'ordinal number');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 2, 'day of a month');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 3, 'mark');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 4, 'sign');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 5, 'business establishment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 6, 'size');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 7, 'ship suffix');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 8, 'horn (wind instrument)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 9, 'bugle call');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 10, 'assumed name');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 11, 'to take a pulse');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (106, 12, 'classifier used to indicate number of people');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (107, 1, 'to drink');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (107, 2, 'variant of 嗬');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (108, 1, 'to shout');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (109, 1, 'old variant of 和');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (110, 1, 'surname He');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 1, '(joining two nouns) and; together with; with (Taiwan pr. [hàn])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 2, '(math.) sum');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 3, 'to make peace');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 4, '(sports) to draw; to tie');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 5, '(bound form) harmonious');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (111, 6, '(bound form) Japan; Japanese');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (112, 1, 'to compose a poem in reply (to sb''s poem) using the same rhyme sequence');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (112, 2, 'to join in the singing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (112, 3, 'to chime in with others');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (113, 1, 'to complete a set in mahjong or playing cards');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (114, 1, 'to combine a powdery substance (flour, plaster etc) with water');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (114, 2, 'Taiwan pr. [huò]');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (115, 1, 'to mix (ingredients) together');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (115, 2, 'to blend');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (115, 3, 'classifier for rinses of clothes');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (115, 4, 'classifier for boilings of medicinal herbs');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (116, 1, 'old variant of 和');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (116, 2, 'harmonious');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (117, 1, '(adverb of degree)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (117, 2, 'quite');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (117, 3, 'very');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (117, 4, 'awfully');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (118, 1, 'surname Hou');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (119, 1, 'empress');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (119, 2, 'queen');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (119, 3, '(archaic) monarch');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (119, 4, 'ruler');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 1, 'back');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 2, 'behind');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 3, 'rear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 4, 'afterwards');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 5, 'after');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 6, 'later');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (120, 7, 'post-');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 1, 'to circle');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 2, 'to go back');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 3, 'to turn around');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 4, 'to answer');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 5, 'to return');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 6, 'to revolve');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 7, 'Hui ethnic group (Chinese Muslims)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 8, 'time');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 9, 'classifier for acts of a play');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (121, 10, 'section or chapter (of a classic book)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (122, 1, 'to curve');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (122, 2, 'to return');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (122, 3, 'to revolve');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (123, 1, 'variant of 回');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 1, 'can; to have the skill; to know how to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 2, 'to be likely to; to be sure to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 3, 'to meet; to get together');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 4, 'meeting; gathering');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 5, '(suffix) union; group; association');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (124, 6, '(bound form) a moment (Taiwan pr. [huǐ])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (125, 1, 'to balance an account');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (125, 2, 'accounting');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (125, 3, 'accountant');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (126, 1, 'train');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (127, 1, '(chicken) egg');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (127, 2, 'hen''s egg');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (128, 1, 'small table');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (129, 1, 'almost');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (130, 1, 'how much');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (130, 2, 'how many');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (130, 3, 'several');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (130, 4, 'a few');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (131, 1, 'used in 家伙 and 家俱');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 1, 'home');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 2, 'family');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 3, '(polite) my (sister, uncle etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 4, 'classifier for families or businesses');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 5, 'refers to the philosophical schools of pre-Han China');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (132, 6, 'noun suffix for a specialist in some activity, such as a musician or revolutionary, corresponding to English -ist, -er, -ary or -ian');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (133, 1, 'family member');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (133, 2, '(old) servant');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 1, 'to see');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 2, 'to meet');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 3, 'to appear (to be sth)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 4, 'to interview');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 5, 'opinion');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (134, 6, 'view');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (135, 1, 'to appear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (135, 2, 'also written 现');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (136, 1, 'item');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (136, 2, 'component');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (136, 3, 'classifier for events, things, clothes etc');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (137, 1, 'dumpling');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (137, 2, 'pot-sticker');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 1, 'to shout');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 2, 'to call');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 3, 'to order');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 4, 'to ask');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 5, 'to be called');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (138, 6, 'by (indicates agent in the passive mood)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (139, 1, 'variant of 叫');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (140, 1, 'older sister');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (141, 1, 'this year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (142, 1, 'today');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (142, 2, 'at the present');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (142, 3, 'now');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (143, 1, 'nine');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (143, 2, '9');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (144, 1, 'to think that ...; to feel that ...');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (144, 2, 'to feel (uncomfortable etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 1, 'to open (transitive or intransitive)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 2, '(of ships, vehicles, troops etc) to start');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 3, 'to turn on; to put in operation; to operate; to run');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 4, 'to boil');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 5, 'to write out (a prescription, check, invoice etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 6, '(directional complement) away; off');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 7, 'carat (gold)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 8, 'abbr. for Kelvin, 开尔文');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (145, 9, 'abbr. for 开本, book format');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (146, 1, 'to drive a car');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (147, 1, 'to look after');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (147, 2, 'to take care of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (147, 3, 'to watch');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (147, 4, 'to guard');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 1, 'to see; to look at');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 2, 'to read');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 3, 'to watch');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 4, 'to visit; to call on');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 5, 'to consider; to regard as');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 6, 'to look after');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 7, 'to treat (a patient or illness)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 8, 'to depend on');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 9, 'to feel (that)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 10, '(after a verb) to give it a try');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (148, 11, 'to watch out for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (149, 1, 'to visit a doctor');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (149, 2, 'to see a patient');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (150, 1, 'to see');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (150, 2, 'to catch sight of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 1, 'can');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 2, 'may');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 3, 'possible');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 4, 'able to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 5, 'not bad');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (151, 6, 'pretty good');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 1, 'subject');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 2, 'course');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 3, 'class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 4, 'lesson');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 5, 'to levy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 6, 'tax');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (152, 7, 'form of divination');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (153, 1, 'mouth');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (153, 2, 'classifier for things with mouths (people, domestic animals, cannons, wells etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (153, 3, 'classifier for bites or mouthfuls');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (154, 1, 'lump; chunk; piece');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (154, 2, 'classifier for pieces of cloth, cake, soap etc');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (154, 3, '(coll.) classifier for money and currency units');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 1, 'to come');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 2, '(used as a substitute for a more specific verb)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 3, 'hither (directional complement for motion toward the speaker, as in 回来)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 4, 'ever since (as in 自古以来)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 5, 'for the past (amount of time)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 6, '(prefix) the coming ...; the next ... (as in 来世)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 7, '(between two verbs) in order to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 8, '(after a round number) approximately');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (155, 9, '(used after 得 to indicate possibility, as in 谈得来, or after 不 to indicate impossibility, as in 吃不来)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (156, 1, 'teacher');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (157, 1, '(completed action marker)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (157, 2, '(modal particle indicating change of state, situation now)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (157, 3, '(modal particle intensifying preceding clause)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (158, 1, 'to finish');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (158, 2, 'to achieve');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (158, 3, 'variant of 了');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (158, 4, 'to understand clearly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (159, 1, '(of eyes) bright');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (159, 2, 'clear-sighted');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (159, 3, 'to understand clearly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (160, 1, 'unofficial variant of 瞭');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (161, 1, 'surname Leng');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (162, 1, 'cold');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (163, 1, 'variant of 里');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (164, 1, 'lining');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (164, 2, 'interior');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (164, 3, 'inside');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (164, 4, 'internal');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (164, 5, 'also written 里');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (165, 1, 'Li (surname)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (166, 1, 'li, ancient measure of length, approx. 500 m');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (166, 2, 'neighborhood');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (166, 3, 'ancient administrative unit of 25 families');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (166, 4, '(Tw) borough, administrative unit between the township 镇 and neighborhood 邻 levels');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (167, 1, 'two');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (167, 2, 'both');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (167, 3, 'some');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (167, 4, 'a few');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (167, 5, 'tael, unit of weight equal to 50 grams (modern) or 1⁄16 of a catty 斤 (old)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 1, 'zero');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 2, 'nought');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 3, 'zero sign');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 4, 'fractional');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 5, 'fragmentary');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 6, 'odd (of numbers)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 7, '(placed between two numbers to indicate a smaller quantity followed by a larger one)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 8, 'fraction');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 9, '(in mathematics) remainder (after division)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 10, 'extra');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 11, 'to wither and fall');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (168, 12, 'to wither');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (169, 1, 'six');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (169, 2, '6');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (170, 1, 'mama');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (170, 2, 'mommy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (170, 3, 'mother');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (171, 1, '(coll.) what?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (172, 1, 'used in 吗啡');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (173, 1, '(question particle for "yes-no" questions)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (174, 1, 'to buy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (174, 2, 'to purchase');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (175, 1, 'to sell');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (175, 2, 'to betray');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (175, 3, 'to spare no effort');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (175, 4, 'to show off or flaunt');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (176, 1, 'busy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (176, 2, 'hurriedly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (176, 3, 'to hurry');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (176, 4, 'to rush');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (177, 1, 'cat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (177, 2, '(dialect) to hide oneself');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (177, 3, '(coll.) modem');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (178, 1, 'it doesn''t matter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (179, 1, 'haven''t');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (179, 2, 'hasn''t');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (179, 3, 'doesn''t exist');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (179, 4, 'to not have');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (179, 5, 'to not be');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (180, 1, 'younger sister');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (180, 2, 'young woman');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (181, 1, 'plural marker for pronouns, and nouns referring to individuals');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (182, 1, '(cooked) rice');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (183, 1, 'bread');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (184, 1, 'erhua variant of 面条');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (184, 2, 'noodles');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (185, 1, 'name (of a person or thing)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (186, 1, 'next year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (187, 1, 'tomorrow');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (188, 1, 'how');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (188, 2, 'which');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (189, 1, '(emphatic sentence-final particle, used instead of 啊 after a word ending in "n")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (190, 1, 'used in 吒');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (190, 2, 'Taiwan pr. [nuó]');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (191, 1, 'which? (interrogative, followed by classifier or numeral-classifier)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (192, 1, 'where?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (192, 2, 'wherever; anywhere; somewhere');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (192, 3, '(used in rhetorical questions) how can ...?; how could ...?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 1, 'where?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 2, 'somewhere');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 3, 'anywhere');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 4, 'wherever');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 5, 'nowhere (negative answer to question)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 6, 'humble expression denying compliment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (193, 7, 'also written 哪里');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 1, 'where?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 2, 'somewhere');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 3, 'anywhere');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 4, 'wherever');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 5, 'nowhere (negative answer to question)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (194, 6, 'humble expression denying compliment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (195, 1, 'which ones?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (195, 2, 'who?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (195, 3, 'what?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (196, 1, 'surname Na');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (197, 1, 'surname Nuo');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (198, 1, 'variant of 哪');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (199, 1, '(specifier) that; the; those (colloquial pr. [nèi])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (199, 2, '(pronoun) that (referring to persons, things or situations)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (199, 3, 'then (in that case)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (200, 1, '(archaic) many');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (200, 2, 'beautiful');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (200, 3, 'how');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (200, 4, 'old variant of 挪');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (201, 1, 'over there');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (201, 2, 'yonder');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (202, 1, 'there');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (203, 1, 'there; that place');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (204, 1, 'there; that place');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (205, 1, 'those');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (206, 1, 'male');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (206, 2, 'Baron, lowest of five orders of nobility 位');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (207, 1, 'boyfriend');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (208, 1, 'particle indicating that a previously asked question is to be applied to the preceding word ("What about ...?", "And ...?")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (208, 2, 'particle for inquiring about location ("Where is ...?")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (208, 3, 'particle signaling a pause, to emphasize the preceding words and allow the listener time to take them on board ("ok?", "are you with me?")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (208, 4, '(at the end of a declarative sentence) particle indicating continuation of a state or action');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (208, 5, 'particle indicating strong affirmation');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (209, 1, 'woolen material');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (210, 1, 'surname Neng');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (211, 1, 'can');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (211, 2, 'to be able to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (211, 3, 'might possibly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (211, 4, 'ability');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (211, 5, '(physics) energy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (212, 1, 'you (informal, as opposed to courteous 您)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (213, 1, 'you (Note: In Taiwan, 妳 is used to address females, but in mainland China, it is not commonly used. Instead, 你 is used to address both males and females.)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (214, 1, 'you (plural)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (215, 1, 'surname Nian');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (216, 1, 'year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (217, 1, 'grain');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (217, 2, 'harvest (old)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (217, 3, 'variant of 年');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (218, 1, 'you (courteous, as opposed to informal 你)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (219, 1, 'cow''s milk');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (220, 1, 'female');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (220, 2, 'woman');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (220, 3, 'daughter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (221, 1, 'archaic variant of 汝');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (222, 1, 'daughter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (223, 1, 'girlfriend');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (224, 1, 'lady');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (224, 2, 'madam');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (224, 3, 'Miss');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (224, 4, 'Ms');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (225, 1, 'friend');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (226, 1, 'pretty');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (226, 2, 'beautiful');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (227, 1, 'apple');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (228, 1, 'seven');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (228, 2, '7');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (229, 1, 'to get out of bed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (229, 2, 'to get up');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (230, 1, 'thousand');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (231, 1, 'see 秋千');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 1, 'front');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 2, 'forward');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 3, 'ahead');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 4, 'first');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 5, 'top (followed by a number)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 6, 'future');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 7, 'ago');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 8, 'before');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 9, 'BC (e.g. 前293年)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 10, 'former');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (232, 11, 'formerly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (233, 1, 'surname Qian');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (234, 1, 'coin');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (234, 2, 'money');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (234, 3, 'unit of weight, one tenth of a tael 两');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (235, 1, 'to ask');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (235, 2, 'to invite');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (235, 3, 'please (do sth)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (235, 4, 'to treat (to a meal etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (235, 5, 'to request');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (236, 1, 'Excuse me, may I ask...?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 1, 'to go');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 2, 'to go to (a place)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 3, '(of a time etc) last');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 4, 'just passed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 5, 'to send');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 6, 'to remove');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 7, 'to get rid of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 8, 'to reduce');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 9, 'to be apart from in space or time');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 10, 'to die (euphemism)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 11, 'to play (a part)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 12, '(when used either before or after a verb) to go in order to do sth');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 13, '(after a verb of motion indicates movement away from the speaker)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (237, 14, '(used after certain verbs to indicate detachment or separation)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (238, 1, 'last year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (239, 1, 'to warm up');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (239, 2, 'to heat up');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (239, 3, 'hot (of weather)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (239, 4, 'heat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (239, 5, 'fervent');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (240, 1, 'person; people');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 1, 'to know');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 2, 'to recognize');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 3, 'to be familiar with');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 4, 'to get acquainted with sb');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 5, 'knowledge');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 6, 'understanding');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 7, 'awareness');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (241, 8, 'cognition');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (242, 1, 'abbr. for 本, Japan');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (243, 1, 'sun');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (243, 2, 'day');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (243, 3, 'date, day of the month');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (244, 1, 'surname San');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (245, 1, 'three');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (245, 2, '3');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (246, 1, 'store; shop');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (247, 1, 'used in 上声');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 1, '(bound form) up; upper; above; previous');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 2, 'first (of multiple parts)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 3, 'to climb; to get onto; to go up');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 4, 'to attend (class or university)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 5, '(directional complement) up');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (248, 6, '(noun suffix) on; above');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (249, 1, 'to go to work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (249, 2, 'to be on duty');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (249, 3, 'to start work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (249, 4, 'to go to the office');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (250, 1, 'to go to class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (250, 2, 'to attend class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (250, 3, 'to go to teach a class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (251, 1, 'morning');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (252, 1, 'to go to school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (252, 2, 'to attend school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 1, 'few');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 2, 'less');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 3, 'to lack');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 4, 'to be missing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 5, 'to stop (doing sth)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (253, 6, 'seldom');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (254, 1, 'young');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (255, 1, 'what?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (255, 2, 'something');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (255, 3, 'anything');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (256, 1, 'to fall ill');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (257, 1, 'ten');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (257, 2, '10');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (258, 1, 'time');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (258, 2, 'length of time');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (258, 3, 'moment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (258, 4, 'period');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (259, 1, 'time');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (259, 2, 'period');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (260, 1, 'matter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (260, 2, 'thing');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (260, 3, 'item');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (260, 4, 'work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (260, 5, 'affair');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (261, 1, 'to be (followed by substantives only)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (261, 2, 'correct; right; true');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (261, 3, '(respectful acknowledgement of a command) very well');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (261, 4, '(adverb for emphatic assertion)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (262, 1, 'variant of 是');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (263, 1, 'cell phone');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (263, 2, 'mobile phone');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (264, 1, 'abbr. for 书经');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (265, 1, 'book');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (265, 2, 'letter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (265, 3, 'document');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (265, 4, 'to write');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (266, 1, 'bookstore');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (267, 1, 'who');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (267, 2, 'also pr. [shuí]');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (268, 1, 'surname Shui');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 1, 'water');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 2, 'river');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 3, 'liquid');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 4, 'beverage');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 5, 'additional charges or income');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (269, 6, '(of clothes) classifier for number of washes');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (270, 1, 'fruit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (271, 1, 'to sleep');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (271, 2, 'to lie down');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (272, 1, 'to go to bed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (272, 2, 'to sleep');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (273, 1, 'to persuade');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (274, 1, 'to speak; to talk; to say');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (274, 2, 'to explain; to comment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (274, 3, 'to scold; to tell off');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (274, 4, '(bound form) theory; doctrine');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (275, 1, 'variant of 说');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 1, 'to speak');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 2, 'to say');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 3, 'to talk');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 4, 'to gossip');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 5, 'to tell stories');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 6, 'talk');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (276, 7, 'word');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (277, 1, 'four');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (277, 2, '4');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (278, 1, 'variant of 岁, year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (278, 2, 'years old');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (279, 1, 'classifier for years (of age)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (279, 2, 'year');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (279, 3, 'year (of crop harvests)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (280, 1, 'he; him (used for either sex when the sex is unknown or unimportant)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (280, 2, '(used before sb''s name for emphasis)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (280, 3, '(used as a meaningless mock object)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (280, 4, '(literary) other');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (281, 1, 'they');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (282, 1, 'it');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (283, 1, 'they (for inanimate objects)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (284, 1, 'she');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (285, 1, 'they');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (285, 2, 'them (for females)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (286, 1, 'highest');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (286, 2, 'greatest');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (286, 3, 'too (much)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (286, 4, 'very');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (286, 5, 'extremely');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (287, 1, 'day');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (287, 2, 'sky');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (287, 3, 'heaven');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (288, 1, 'weather');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (289, 1, 'smile (archaic)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 1, 'to listen to; to hear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 2, 'to heed; to obey');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 3, 'a can (loanword from English "tin")');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 4, 'classifier for canned beverages');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 5, 'to let be; to allow (Taiwan pr. [tìng])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (290, 6, '(literary) to administer; to deal with (Taiwan pr. [tìng])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (291, 1, 'to hear');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (292, 1, 'to study at the same school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (292, 2, 'fellow student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (292, 3, 'classmate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (293, 1, 'outside');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (293, 2, 'in addition');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (293, 3, 'foreign');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (293, 4, 'external');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (294, 1, 'outside');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (294, 2, 'outer surface');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (294, 3, 'abroad');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (294, 4, 'place other than one''s home');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 1, 'to play');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 2, 'to have fun');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 3, 'to trifle with');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 4, 'toy');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 5, 'sth used for amusement');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 6, 'curio or antique (Taiwan pr. [wàn])');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (295, 7, 'to keep sth for entertainment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (296, 1, 'variant of 玩');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (296, 2, 'Taiwan pr. [wàn]');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (297, 1, 'evening');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (297, 2, 'night');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (297, 3, 'late');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (298, 1, 'evening meal');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (298, 2, 'dinner');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (298, 3, 'supper');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (299, 1, 'evening');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (299, 2, 'night');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (299, 3, 'in the evening');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (300, 1, 'hello (when answering the phone)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (301, 1, 'hey');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (301, 2, 'to feed (an animal, baby, invalid etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (302, 1, 'variant of 喂');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (303, 1, 'to feed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (304, 1, 'to ask; to inquire');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (305, 1, 'question');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (305, 2, 'problem');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (305, 3, 'issue');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (305, 4, 'topic');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (306, 1, 'I; me; my');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (307, 1, 'we');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (307, 2, 'us');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (307, 3, 'ourselves');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (307, 4, 'our');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (308, 1, 'five');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (308, 2, '5');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (309, 1, 'lunch');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (310, 1, 'to like; to be fond of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 1, 'down');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 2, 'downwards');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 3, 'below');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 4, 'lower');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 5, 'later');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 6, 'next (week etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 7, 'second (of two parts)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 8, 'to decline');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 9, 'to go down');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 10, 'to arrive at (a decision, conclusion etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (311, 11, 'measure word to show the frequency of an action');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (312, 1, 'to finish work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (312, 2, 'to get off work');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (313, 1, 'to finish class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (313, 2, 'to get out of class');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (313, 3, '(fig.) (esp. of a sports coach) to be dismissed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (313, 4, 'to be fired');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (314, 1, 'afternoon');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (314, 2, 'p.m.');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (315, 1, 'to rain');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (316, 1, 'teacher');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (316, 2, 'gentleman; sir; mister (Mr.)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (316, 3, 'husband');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (316, 4, '(dialect) doctor');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 1, 'now');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 2, 'at present');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 3, 'at the moment');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 4, 'modern');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 5, 'current');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (317, 6, 'nowadays');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (318, 1, 'to think (about)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (318, 2, 'to think of; to devise');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (318, 3, 'to think (that); to believe (that)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (318, 4, 'to desire; to want (to)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (318, 5, 'to miss (feel wistful about the absence of)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (319, 1, 'small');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (319, 2, 'tiny');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (319, 3, 'few');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (319, 4, 'young');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (320, 1, 'child');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (321, 1, 'hour');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (322, 1, 'elementary school; primary school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (323, 1, 'primary school student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (323, 2, 'schoolchild');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (323, 3, '(fig.) beginner');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (324, 1, 'classifier indicating a small amount or small number greater than 1: some, a few, several');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (325, 1, 'to write');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (326, 1, 'to thank');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (326, 2, 'thanks');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (326, 3, 'thank you');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (327, 1, 'abbr. for Xinjiang 疆 or Singapore 坡');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (327, 2, 'surname Xin');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (328, 1, 'new');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (328, 2, 'newly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (328, 3, 'meso- (chemistry)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (329, 1, 'week');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (329, 2, 'day of the week');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (329, 3, 'Sunday');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (330, 1, 'Sunday');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (331, 1, 'Sunday');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (332, 1, 'rest');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (332, 2, 'to rest');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (333, 1, 'to learn');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (333, 2, 'to study');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (333, 3, 'to imitate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (333, 4, 'science');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (333, 5, '-ology');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (334, 1, 'student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (334, 2, 'schoolchild');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (335, 1, 'to learn');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (335, 2, 'to study');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (336, 1, 'school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (337, 1, 'surname Xue');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (338, 1, 'snow');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (338, 2, '(literary) to wipe away (a humiliation etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (339, 1, '(bound form) to demand; to coerce');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (340, 1, 'to want; to need; to ask for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (340, 2, 'will; shall; about to');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (340, 3, 'need to; should');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (340, 4, 'if (same as 是)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (340, 5, '(bound form) important');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (341, 1, 'surname Ye');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (342, 1, '(adverb) also; both ... and ... (before predicates only)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (342, 2, '(literary) particle having functions similar to 啊');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 1, 'one');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 2, 'single');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 3, 'a (article)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 4, 'as soon as');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 5, 'entire; whole; all; throughout');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 6, '"one" radical in Chinese characters (Kangxi radical 1)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (343, 7, 'also pr. [yāo] for greater clarity when spelling out numbers digit by digit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (344, 1, 'half');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (345, 1, 'erhua variant of 一点');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (345, 2, 'a bit; a little bit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (345, 3, '(used in negative expressions) (not) the least bit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (345, 4, '(after an adjective, used to form the comparative) a bit more');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (346, 1, 'some');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (346, 2, 'a few');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (346, 3, 'a little');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (346, 4, '(following an adjective) slightly ...er');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (347, 1, 'clothes');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (348, 1, 'doctor');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (349, 1, 'hospital');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (350, 1, 'chair');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (351, 1, 'to have; there is');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (351, 2, '(bound form) having; with; -ful; -ed; -al (as in 意 intentional)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (352, 1, '(there are) some (who are...)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (352, 2, 'some (exist)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (353, 1, 'slightly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (353, 2, 'a little');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (353, 3, 'somewhat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (354, 1, 'some');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (354, 2, 'somewhat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (355, 1, 'rain');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (356, 1, '(literary) to rain');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (356, 2, '(of rain, snow etc) to fall');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (356, 3, 'to precipitate');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (356, 4, 'to wet');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (357, 1, 'surname Yuan');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (357, 2, 'the Yuan or Mongol dynasty (1279-1368)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 1, 'currency unit (esp. Chinese yuan)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 2, 'first');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 3, 'original');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 4, 'primary');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 5, 'fundamental');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 6, 'constituent');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 7, 'part');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 8, 'era (of a reign)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 9, 'meta- (prefix)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 10, '(math.) argument');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 11, 'variable');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (358, 12, '(Tw) (geology) eon');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (359, 1, 'moon');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (359, 2, 'month');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (359, 3, 'monthly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (360, 1, 'again; once more; re-');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (360, 2, 'second; another');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (360, 3, 'then (after sth, and not until then)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (360, 4, 'no matter how ... (followed by an adjective or verb, and then (usually) 也 or 都 for emphasis)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (361, 1, 'goodbye');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (361, 2, 'see you again later');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (362, 1, 'to exist; to be alive');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (362, 2, '(of sb or sth) to be (located) at');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (362, 3, '(used before a verb to indicate an action in progress)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (363, 1, 'early');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (363, 2, 'morning');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (363, 3, 'Good morning!');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (363, 4, 'long ago');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (363, 5, 'prematurely');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (364, 1, 'breakfast');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (365, 1, 'early morning');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (366, 1, 'how?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (366, 2, 'what?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (366, 3, 'why?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (367, 1, 'variant of 怎么');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (368, 1, 'how?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (368, 2, 'how about?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (368, 3, 'how was it?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (368, 4, 'how are things?');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 1, 'to try to find');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 2, 'to look for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 3, 'to call on sb');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 4, 'to find');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 5, 'to seek');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 6, 'to return');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (369, 7, 'to give change');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (370, 1, '(pronoun) this; these');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (370, 2, '(bound form) this; the (followed by a noun)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (370, 3, '(bound form) this; these (followed by a classifier) (in this sense, commonly pr. [zhèi], esp. in Beijing)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (371, 1, 'this side');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (371, 2, 'here');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (372, 1, 'here');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (373, 1, 'variant of 这里');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (374, 1, 'here');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (375, 1, 'these');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 1, 'really');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 2, 'truly');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 3, 'indeed');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 4, 'real');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 5, 'true');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (376, 6, 'genuine');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (377, 1, 'just at (that time)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (377, 2, 'right in (that place)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (377, 3, 'right in the middle of (doing sth)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (378, 1, 'to know; to become aware of');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (378, 2, 'also pr. [zhī dao]');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (379, 1, 'only');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (379, 2, 'merely');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (379, 3, 'just');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (379, 4, 'but');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (380, 1, 'variant of 只');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (381, 1, 'grain that has begun to ripen');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (382, 1, 'variant of 只');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (383, 1, 'classifier for birds and certain animals, one of a pair, some utensils, vessels etc');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (384, 1, 'China');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (385, 1, 'Chinese language');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (386, 1, 'noon');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (386, 2, 'midday');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (387, 1, 'middle school');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (388, 1, 'middle-school student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (388, 2, 'high school student');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 1, 'to live');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 2, 'to dwell');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 3, 'to stay');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 4, 'to reside');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 5, 'to stop');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (389, 6, '(suffix indicating firmness, steadiness, or coming to a halt)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (390, 1, 'table');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (390, 2, 'desk');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (391, 1, 'letter');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (391, 2, 'symbol');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (391, 3, 'character');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (391, 4, 'word');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (391, 5, 'courtesy or style name traditionally given to males aged 20 in dynastic China');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (392, 1, 'yesterday');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (393, 1, 'surname Zuo');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (394, 1, 'to sit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (394, 2, 'to take a seat');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (394, 3, 'to take (a bus, airplane etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (394, 4, 'to bear fruit');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (394, 5, 'variant of 座');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 1, 'to make; to produce');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 2, 'to write; to compose');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 3, 'to do; to engage in; to hold (a party etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 4, '(of a person) to be (an intermediary, a good student etc); to become (husband and wife, friends etc)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 5, '(of a thing) to serve as; to be used for');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (395, 6, 'to assume (an air or manner)');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (396, 1, 'to prepare a meal');

INSERT INTO vocabulary_meaning (reading_id, position, meaning) VALUES (396, 2, 'to cook');

COMMIT;
