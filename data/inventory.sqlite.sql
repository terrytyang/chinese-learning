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

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (1, '百', '百', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (2, '日', '日', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (3, '兴', '興', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (4, '爱', '愛', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (5, '系', '係', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (6, '元', '元', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (7, '西', '西', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (8, '弟', '弟', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (9, '期', '朞', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (10, '您', '您', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (11, '四', '四', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (12, '欢', '歡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (13, '外', '外', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (14, '喂', '喂', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (15, '手', '手', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (16, '士', '士', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (17, '菜', '菜', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (18, '零', '零', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (19, '对', '對', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (20, '要', '要', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (21, '快', '快', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (22, '错', '錯', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (23, '每', '每', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (24, '步', '步', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (25, '已', '已', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (26, '室', '室', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (27, '但', '但', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (28, '药', '葯', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (29, '运', '運', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (30, '比', '比', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (31, '虽', '雖', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (32, '思', '思', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (33, '自', '自', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (34, '画', '畫', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (35, '跟', '跟', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (36, '绿', '綠', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (37, '等', '等', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (38, '最', '㝡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (39, '跑', '跑', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (40, '己', '己', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (41, '聪', '聰', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (42, '总', '總', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (43, '北', '北', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (44, '牙', '牙', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (45, '扫', '掃', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (46, '员', '員', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (47, '空', '空', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (48, '受', '受', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (49, '乎', '乎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (50, '凉', '涼', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (51, '矿', '礦', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (52, '查', '查', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (53, '算', '算', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (54, '嘴', '嘴', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (55, '腿', '腿', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (56, '又', '又', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (57, '声', '聲', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (58, '姨', '姨', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (59, '板', '板', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (60, '直', '直', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (61, '伤', '傷', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (62, '招', '招', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (63, '骄', '驕', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (64, '装', '裝', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (65, '勇', '勇', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (66, '围', '圍', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (67, '丽', '麗', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (68, '庭', '庭', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (69, '烟', '煙', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (70, '破', '破', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (71, '严', '嚴', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (72, '与', '與', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (73, '频', '頻', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (74, '巴', '巴', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (75, '傅', '傅', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (76, '拉', '拉', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (77, '疑', '疑', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (78, '误', '誤', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (79, '递', '遞', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (80, '赚', '賺', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (81, '烈', '烈', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (82, '软', '軟', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (83, '占', '佔', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (84, '阻', '阻', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (85, '敬', '敬', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (86, '乏', '乏', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (87, '慎', '慎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (88, '丑', '丑', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (89, '叉', '叉', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (90, '逐', '逐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (91, '穷', '窮', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (92, '漏', '漏', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (93, '补', '補', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (94, '代', '代', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (95, '巨', '巨', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (96, '亏', '虧', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (97, '魅', '魅', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (98, '辞', '辤', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (99, '墙', '墻', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (100, '碌', '碌', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (101, '撑', '撐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (102, '跃', '躍', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (103, '循', '循', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (104, '棋', '棊', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (105, '拔', '拔', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (106, '丧', '喪', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (107, '庞', '龐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (108, '嫁', '嫁', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (109, '坛', '壇', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (110, '酱', '醬', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (111, '罐', '罐', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (112, '耗', '耗', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (113, '恶', '惡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (114, '圈', '圈', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (115, '迫', '迫', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (116, '庄', '莊', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (117, '核', '核', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (118, '祖', '祖', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (119, '扎', '扎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (120, '睁', '睜', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (121, '愚', '愚', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (122, '梢', '梢', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (123, '恒', '恆', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (124, '倦', '倦', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (125, '倘', '倘', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (126, '酌', '酌', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (127, '陡', '陡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (128, '阐', '闡', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (129, '钩', '鈎', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (130, '亭', '亭', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (131, '陈', '陳', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (132, '钙', '鈣', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (133, '盏', '盞', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (134, '炖', '燉', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (135, '楷', '楷', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (136, '畔', '畔', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (137, '嘈', '嘈', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (138, '蘸', '蘸', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (139, '驭', '馭', NULL, NULL);

INSERT INTO hanzi_character (id, simplified, traditional, english_gloss, usage_note) VALUES (140, '芬', '芬', NULL, NULL);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (1, 'new', 'HSK 3.0 (2021 standard)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (2, 'newest', 'HSK 3.0 (2026 syllabus)', 7);

INSERT INTO hsk_scheme (id, code, label, max_level) VALUES (3, 'old', 'HSK 2.0', 6);

INSERT INTO learning_status (id, code, label) VALUES (1, 'not_encountered', 'Not yet encountered');

INSERT INTO learning_status (id, code, label) VALUES (2, 'learning', 'Learning');

INSERT INTO learning_status (id, code, label) VALUES (3, 'known', 'Known');

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (1, 3, 2);

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

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (6, 3, 2);

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

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (10, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (11, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (12, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (13, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (14, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (15, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (16, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (17, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (18, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (19, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 2, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (20, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (21, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (22, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (23, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (24, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (25, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (26, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (27, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (28, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (29, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (30, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (31, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (32, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (33, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (34, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (35, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (36, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (37, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (38, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (39, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 2, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (40, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (41, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (42, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 1, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (43, 3, 1);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (44, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (45, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (46, 3, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (47, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (48, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (49, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (50, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (51, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (52, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (53, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (54, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (55, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (56, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (57, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (58, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (59, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 2, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (60, 3, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (61, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (62, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (63, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (64, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (65, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (66, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (67, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (68, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (69, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (70, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (71, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (72, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (73, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (74, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (75, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (76, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (77, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (78, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (79, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 2, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (80, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (81, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (82, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (83, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (84, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (85, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (86, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (87, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (88, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (89, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (90, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (91, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (92, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (93, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 1, 3);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (94, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (95, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (96, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (97, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (98, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 1, 2);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (99, 3, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 2, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (100, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (101, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (102, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (103, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (104, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (105, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (106, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (107, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (108, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (109, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (110, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (111, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (112, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (113, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (114, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 1, 4);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (115, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (116, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 1, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (117, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (118, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 1, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (119, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 2, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (120, 3, 5);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (121, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (122, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (123, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (124, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (125, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (126, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (127, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (128, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (129, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (130, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (131, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (132, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (132, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (133, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (133, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (134, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (134, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (135, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (135, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (136, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (137, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (137, 3, 6);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (138, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (138, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (139, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (139, 2, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (140, 1, 7);

INSERT INTO character_hsk_level (character_id, hsk_scheme_id, level) VALUES (140, 2, 7);

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

COMMIT;
