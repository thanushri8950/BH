import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    category TEXT,
    available INTEGER,
    issue_date TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")
