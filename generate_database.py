import json
import sqlite3
import random
import string
import bcrypt

def generate_password(username_to_password):
    password = f"{username_to_password}123"
    # If you want to check password easier, comment out row 10-13 (this will make it so the db displays the actual passwords)
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    password =  hash
    return password


with open("data-sample-small.json", "r", encoding="utf-8") as f:
    data = json.load(f)

con = sqlite3.connect("database.db")
con.execute("PRAGMA foreign_keys = ON;")
cur = con.cursor()

cur.executescript("""
DROP TABLE IF EXISTS snapshot_taxonomy;
DROP TABLE IF EXISTS snapshots;
DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS learning_goal_keywords;
DROP TABLE IF EXISTS entry_learning_goals;
DROP TABLE IF EXISTS learning_goals;
DROP TABLE IF EXISTS entry_taxonomy_scale;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS subjects;

CREATE TABLE teachers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  e_mail TEXT NOT NULL,
  password TEXT NOT NULL               
);

CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  klas TEXT NOT NULL,
  e_mail TEXT NOT NULL,
  password TEXT NOT NULL 
);

CREATE TABLE subjects (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  subject_id INTEGER NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(subject_id) REFERENCES subjects(id)
);

CREATE TABLE entry_taxonomy_scale (
  entry_id INTEGER NOT NULL,
  position INTEGER NOT NULL,
  level TEXT NOT NULL,
  PRIMARY KEY(entry_id, position),
  FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE TABLE learning_goals (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL
);

CREATE TABLE entry_learning_goals (
  entry_id INTEGER NOT NULL,
  learning_goal_id TEXT NOT NULL,
  PRIMARY KEY(entry_id, learning_goal_id),
  FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE,
  FOREIGN KEY(learning_goal_id) REFERENCES learning_goals(id)
);

CREATE TABLE learning_goal_keywords (
  learning_goal_id TEXT NOT NULL,
  keyword TEXT NOT NULL,
  PRIMARY KEY(learning_goal_id, keyword),
  FOREIGN KEY(learning_goal_id) REFERENCES learning_goals(id) ON DELETE CASCADE
);

CREATE TABLE sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,
  external_id TEXT NOT NULL,
  UNIQUE(type, external_id)
);

CREATE TABLE snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  learning_goal_id TEXT NOT NULL,
  at TEXT NOT NULL,
  source_id INTEGER,
  FOREIGN KEY(learning_goal_id) REFERENCES learning_goals(id) ON DELETE CASCADE,
  FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE snapshot_taxonomy (
  snapshot_id INTEGER NOT NULL,
  level TEXT NOT NULL,
  kennen REAL,
  kunnen REAL,
  confidence REAL,
  PRIMARY KEY(snapshot_id, level),
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
);
""")

def get_source_id(source_type, external_id):
    if source_type is None or external_id is None:
        return None
    cur.execute(
        "INSERT OR IGNORE INTO sources(type, external_id) VALUES(?, ?)",
        (source_type, external_id),
    )
    cur.execute(
        "SELECT id FROM sources WHERE type=? AND external_id=?",
        (source_type, external_id),
    )
    return cur.fetchone()[0]

example_teacher = 'John'

with con:
    cur.execute("SELECT COUNT(*) FROM teachers")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO teachers(id, name, e_mail, password) VALUES(?, ?, ?, ?)",
            (
                1,
                example_teacher,
                example_teacher + '@gmail.com',
                generate_password(example_teacher),
            ),
        )

    for entry in data.get("entries", []):
        student = entry.get("student") or {}
        subject = entry.get("subject") or {}

        student_id = int(student.get("id"))
        subject_id = int(subject.get("id"))

        klas = student.get("klas")
        if not klas:
            klas = random.choice(["1A", "1B", "1C"])

        cur.execute(
            "INSERT INTO students(id, name, klas, e_mail, password) VALUES(?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, klas=excluded.klas",
            (student_id, student.get("name") or "", klas, student.get("name")+'@gmail.com',generate_password(student.get("name")), ),
        )

        cur.execute(
            "INSERT INTO subjects(id, name) VALUES(?, ?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name",
            (subject_id, subject.get("name") or ""),
        )

        cur.execute(
            "INSERT INTO entries(student_id, subject_id) VALUES(?, ?)",
            (student_id, subject_id),
        )
        entry_id = cur.lastrowid

        for position, level in enumerate(entry.get("taxonomyScale") or []):
            cur.execute(
                "INSERT INTO entry_taxonomy_scale(entry_id, position, level) VALUES(?, ?, ?)",
                (entry_id, position, level),
            )

        for learning_goal in entry.get("learningGoals") or []:
            learning_goal_id = learning_goal.get("id")

            cur.execute(
                "INSERT INTO learning_goals(id, title) VALUES(?, ?) "
                "ON CONFLICT(id) DO UPDATE SET title=excluded.title",
                (learning_goal_id, learning_goal.get("title") or ""),
            )

            cur.execute(
                "INSERT OR IGNORE INTO entry_learning_goals(entry_id, learning_goal_id) VALUES(?, ?)",
                (entry_id, learning_goal_id),
            )

            for keyword in learning_goal.get("keywords") or []:
                cur.execute(
                    "INSERT OR IGNORE INTO learning_goal_keywords(learning_goal_id, keyword) VALUES(?, ?)",
                    (learning_goal_id, keyword),
                )

            for snapshot in learning_goal.get("snapshots") or []:
                source = snapshot.get("source") or {}
                source_id = get_source_id(source.get("type"), source.get("id"))

                cur.execute(
                    "INSERT INTO snapshots(learning_goal_id, at, source_id) VALUES(?, ?, ?)",
                    (learning_goal_id, snapshot.get("at") or "", source_id),
                )
                snapshot_id = cur.lastrowid

                for taxonomy_item in snapshot.get("taxonomy") or []:
                    cur.execute(
                        "INSERT INTO snapshot_taxonomy(snapshot_id, level, kennen, kunnen, confidence) "
                        "VALUES(?, ?, ?, ?, ?)",
                        (
                            snapshot_id,
                            taxonomy_item.get("level"),
                            taxonomy_item.get("kennen"),
                            taxonomy_item.get("kunnen"),
                            taxonomy_item.get("confidence"),
                        ),
                    )

con.close()