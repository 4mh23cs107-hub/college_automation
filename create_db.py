import os
from app import app, db, User, Student, Subject
from dotenv import load_dotenv

load_dotenv()


def init_sqlite():
    # use application context so SQLAlchemy can access current_app
    with app.app_context():
        db.create_all()
        seed_basic()

def seed_basic():
    # Create roles if not exist
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin', role='Admin')
            u.set_password('adminpass')
            db.session.add(u)
        if not User.query.filter_by(username='hod').first():
            h = User(username='hod', role='HOD')
            h.set_password('hodpass')
            db.session.add(h)
        if not User.query.filter_by(username='fac1').first():
            f = User(username='fac1', role='Faculty')
            f.set_password('facpass')
            db.session.add(f)
        # sample student user: username will be USN
        if not User.query.filter_by(username='1PV16CS001').first():
            suser = User(username='1PV16CS001', role='Student')
            suser.set_password('studpass')
            db.session.add(suser)
        # sample student record
        if not Student.query.filter_by(usn='1PV16CS001').first():
            student = Student(usn='1PV16CS001', name='John Doe', dept='CSE', semester=6)
            db.session.add(student)
        # sample subjects
        if not Subject.query.filter_by(code='CS101').first():
            sub = Subject(code='CS101', name='Operating Systems', dept='CSE', semester=6)
            db.session.add(sub)
        if not Subject.query.filter_by(code='CS102').first():
            sub2 = Subject(code='CS102', name='Database Systems', dept='CSE', semester=6)
            db.session.add(sub2)

        db.session.commit()
        print('DB initialized with sample users and data')


def init_postgres(dsn):
    """
    Apply `sql/schema.sql` to the Postgres database and seed demo data via stored procedures.
    """
    try:
        import psycopg2
        from psycopg2 import sql
    except Exception as e:
        print('psycopg2 is required to initialize Postgres schema:', e)
        return

    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), 'sql', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = None
    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(schema_sql)
        print('Applied schema.sql')

        # seed users via stored procedure
        cur.execute("SELECT sp_create_user(%s,%s,%s)", ('admin','adminpass','Admin'))
        cur.execute("SELECT sp_create_user(%s,%s,%s)", ('hod','hodpass','HOD'))
        cur.execute("SELECT sp_create_user(%s,%s,%s)", ('fac1','facpass','Faculty'))
        cur.execute("SELECT sp_create_user(%s,%s,%s)", ('1PV16CS001','studpass','Student'))

        # seed student and subjects using stored functions
        cur.execute("SELECT sp_add_student(%s,%s,%s,%s)", ('1PV16CS001','John Doe','CSE',6))
        cur.execute("SELECT sp_add_subject(%s,%s,%s,%s)", ('CS101','Operating Systems','CSE',6))
        cur.execute("SELECT sp_add_subject(%s,%s,%s,%s)", ('CS102','Database Systems','CSE',6))

        print('Seeded demo data into Postgres')
    except Exception as ex:
        print('Error initializing Postgres schema:', ex)
    finally:
        if conn:
            conn.close()


def init_db():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and ('postgres' in DATABASE_URL or 'postgresql' in DATABASE_URL):
        init_postgres(DATABASE_URL)
    else:
        init_sqlite()


if __name__ == '__main__':
    init_db()
