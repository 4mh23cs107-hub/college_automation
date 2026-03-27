"""Helpers to call stored procedures when using PostgreSQL, otherwise fall back to SQLAlchemy ORM."""
import os
from app import db, User, Student, Subject
from sqlalchemy import text

DATABASE_URL = os.getenv('DATABASE_URL')


def sp_create_user(conn, username, password, role):
    if DATABASE_URL and ('postgres' in DATABASE_URL or 'postgresql' in DATABASE_URL):
        # call stored procedure
        with conn.begin():
            conn.execute(text("SELECT sp_create_user(:u,:p,:r)"), { 'u': username, 'p': password, 'r': role })
    else:
        if not User.query.filter_by(username=username).first():
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()


def sp_add_student(conn, usn, name, dept, semester):
    if DATABASE_URL and ('postgres' in DATABASE_URL or 'postgresql' in DATABASE_URL):
        with conn.begin():
            conn.execute(text("SELECT sp_add_student(:usn,:name,:dept,:sem)"), { 'usn': usn, 'name': name, 'dept': dept, 'sem': semester })
    else:
        if not Student.query.filter_by(usn=usn).first():
            s = Student(usn=usn, name=name, dept=dept, semester=semester)
            db.session.add(s)
            db.session.commit()


# Additional helpers can be added similarly for marks/attendance/assignments
