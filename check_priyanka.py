import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    result = db.execute(text("SELECT usn, name, dept, semester FROM student WHERE usn = 'priyanka'")).first()
    if result:
        print(f"Student 'priyanka' details: USN={result[0]}, Name={result[1]}, Dept='{result[2]}', Sem={result[3]}")
    else:
        print("Student 'priyanka' not found in student table.")
    
    # Also check all students to see if any have dept/sem
    results = db.execute(text("SELECT usn, dept, semester FROM student LIMIT 10")).fetchall()
    print("\nSample Students:")
    for r in results:
        print(r)
finally:
    db.close()
