import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

roll TEXT,

email TEXT,

attendance REAL,

study_hours REAL,

assignment_marks REAL,

quiz_marks REAL,

previous_marks REAL,

participation REAL,

predicted_marks REAL,

grade TEXT,

risk TEXT

)
""")

conn.commit()
conn.close()

print("Database Created Successfully")