--create the database > sqlite3 testdb.sqlite < db_scheme.sql
PRAGMA foreign_keys = ON;
CREATE TABLE word_types (
  id                INTEGER PRIMARY KEY,
  name              TEXT NOT NULL,
  UNIQUE(name)
);

CREATE TABLE word_cases (
  id                INTEGER PRIMARY KEY,
  name              TEXT NOT NULL,
  word_type_id      INTEGER NOT NULL,
  case_order        INTEGER NOT NULL,
  FOREIGN KEY(word_type_id) REFERENCES word_types(id),
  UNIQUE(name, word_type_id)
);

CREATE TABLE groups (
  id                INTEGER PRIMARY KEY
);

CREATE TABLE lectures (
  id                INTEGER PRIMARY KEY,
  name              TEXT NOT NULL,
  UNIQUE(name)
);

CREATE TABLE languages (
  id                INTEGER PRIMARY KEY,
  name              INTEGER NOT NULL,
  translation_order INTEGER NOT NULL
    --doc for translation order: see table 'translations'
);

CREATE TABLE translations (
  id                INTEGER PRIMARY KEY,
  group_lower_translation_order_id    INTEGER NOT NULL,
  group_higher_translation_order_id   INTEGER NOT NULL
    --order may not be changed / group associations in this table shall always
    --be stored with the lower translation order in the column "group_lower_translation_order_id"
);

CREATE TABLE words (
  id                INTEGER PRIMARY KEY,
  name              TEXT NOT NULL,
  irregular         INTEGER,          --BOOL
  learned           INTEGER,          --BOOL
  group_id          INTEGER NOT NULL,
  lecture_id        INTEGER NOT NULL,
  language_id       INTEGER NOT NULL,
  word_case_id      INTEGER NOT NULL,
  FOREIGN KEY(group_id) REFERENCES groups(id),
  FOREIGN KEY(lecture_id) REFERENCES lectures(id),
  FOREIGN KEY(language_id) REFERENCES languages(id),
  FOREIGN KEY(word_case_id) REFERENCES word_cases(id),
  UNIQUE(group_id, word_case_id)
);

INSERT INTO word_types (id, name) VALUES (1, 'verb');
INSERT INTO word_types (id, name)VALUES (2, 'noun');
INSERT INTO word_types (id, name)VALUES (3, 'adjective');
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (1, 'imperative',1, 2);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (2, 'infinitive',1, 1);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (3, 'present tense',1, 3);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (4, 'past tense',1, 4);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (5, 'supine',1, 5);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (6, 'indefinite singular',2, 1);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (7, 'definite singular',2, 2);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (8, 'indefinite plural',2, 3);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (9, 'definite plural',2, 4);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (10, 'en-conjugation',3, 1);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (11, 'ett-conjugation',3, 2);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (12, 'definite and plural',3, 3);
INSERT INTO word_cases (id, name, word_type_id, case_order) VALUES (13, 'plural (irregular)',3, 4);
INSERT INTO languages (id, name, translation_order) VALUES (1, 'German', 10);
INSERT INTO languages (id, name, translation_order) VALUES (2, 'Swedish', 20);
INSERT INTO lectures (id, name) VALUES (1, 'A1, L1');
INSERT INTO lectures (id, name) VALUES (2, 'A1, L2');
INSERT INTO groups (id) VALUES(1),(2),(3);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (1, 'helfen', 1, 1, 1, 2);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (2, 'hjälp', 2, 1, 2, 1);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (3, 'hjälpa', 2, 1, 2, 2);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (4, 'hjälper', 2, 2, 2, 3);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (5, 'hjälpte', 2, 1, 2, 4);
INSERT INTO words (id, name, group_id, lecture_id, language_id, word_case_id) VALUES (6, 'hjälpt', 3, 1, 2, 5);
INSERT INTO translations (id, group_lower_language_order_id, group_higher_language_order_id) VALUES (1, 1, 2);
INSERT INTO translations (id, group_lower_language_order_id, group_higher_language_order_id) VALUES (2, 1, 3);

--Test selects
select * from words where group_id = 2; --ok
select group_higher_language_order_id from translations where group_lower_language_order_id = 1; --ok
--select words of different groups whose translations corresponding to the group_id 1 that belongs to the lower translation order.
select * from words where group_id IN (select group_higher_language_order_id from translations where group_lower_language_order_id = 1); --ok
--select words belonging to lecture 1
select * from words where lecture_id = 1; --ok
--select words to translate that belong to selectet lecture_ids
select * from words where group_id IN (select group_higher_language_order_id from translations where group_lower_language_order_id = 1) and lecture_id = 1; --ok

