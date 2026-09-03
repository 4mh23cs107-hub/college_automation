import sqlite3
import os

db_path = 'college.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(student)")
    columns = cursor.fetchall()
    print("Student Table Columns:")
    for col in columns:
        print(col)
    
    cursor.execute("SELECT * FROM student LIMIT 5")
    rows = cursor.fetchall()
    print("\nStudent Table Data (first 5):")
    for row in rows:
        print(row)

    cursor.execute("PRAGMA table_info(marks)")
    columns = cursor.fetchall()
    print("\nMarks Table Columns:")
    for col in columns:
        print(col)

    cursor.execute("SELECT * FROM marks LIMIT 5")
    rows = cursor.fetchall()
    print("\nMarks Table Data (first 5):")
    for row in rows:
        print(row)

    conn.close()
else:
    print(f"Database {db_path} not found.")
