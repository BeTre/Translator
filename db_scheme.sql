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
  language_id       INTEGER NOT NULL,
  case_order        INTEGER NOT NULL,
  FOREIGN KEY(word_type_id) REFERENCES word_types(id),
  FOREIGN KEY(language_id)  REFERENCES languages(id),
  UNIQUE(name, word_type_id, language_id)
  UNIQUE(word_type_id, language_id, case_order)
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
    --be stored with the lower translation order in the column
    --"group_lower_translation_order_id"
);

CREATE TABLE words (
  id                INTEGER PRIMARY KEY,
  name              TEXT NOT NULL,
  irregular         INTEGER,          --BOOL (True = 1, False = 0)
  learned           INTEGER,          --BOOL (True = 1, False = 0)
  group_id          INTEGER NOT NULL,
  lecture_id        INTEGER NOT NULL,
  language_id       INTEGER NOT NULL,
  word_case_id      INTEGER NOT NULL,
  FOREIGN KEY(group_id)     REFERENCES groups(id),
  FOREIGN KEY(lecture_id)   REFERENCES lectures(id),
  FOREIGN KEY(language_id)  REFERENCES languages(id),
  FOREIGN KEY(word_case_id) REFERENCES word_cases(id),
  UNIQUE(group_id, word_case_id)
);
