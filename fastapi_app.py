import os
import logging
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the engine before usage
DB_PATH = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(os.path.dirname(__file__), "college.db")}')
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if 'sqlite' in DB_PATH else {})

# Define SessionLocal before usage
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure Base is defined before usage
Base = declarative_base()

app = FastAPI(title='College Automation FastAPI')
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'dev-secret'), session_cookie='session')
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

# basic logger to record unhandled exceptions
logger = logging.getLogger('fastapi_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('fastapi_error.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(fh)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    entry = f"\n-----\nTIME: {datetime.utcnow().isoformat()}Z\nPATH: {request.url.path}\n{tb}\n"
    try:
        logger.error(entry)
    except Exception:
        # fallback file write
        with open('fastapi_error.log', 'a', encoding='utf-8') as f:
            f.write(entry)
    # return a simple page that indicates an internal error and where logs are written
    body = f"<h2>Internal Server Error</h2><p>An unexpected error occurred. Details are logged to <code>fastapi_error.log</code>.</p>"
    return HTMLResponse(content=body, status_code=500)


def render_template_safe(name: str, request: Request, context: dict):
    """Render template and log any rendering errors to the error log.

    Returns a TemplateResponse on success or an HTMLResponse with 500 on failure.
    """
    try:
        return templates.TemplateResponse(request, name, context)
    except Exception:
        tb = traceback.format_exc()
        entry = f"\n-----\nTIME: {datetime.utcnow().isoformat()}Z\nTEMPLATE: {name}\nPATH: {request.url.path}\n{tb}\n"
        try:
            logger.error(entry)
        except Exception:
            with open('fastapi_error.log', 'a', encoding='utf-8') as f:
                f.write(entry)
        body = f"<h2>Template rendering error</h2><p>See <code>fastapi_error.log</code> for details.</p>"
        return HTMLResponse(content=body, status_code=500)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, index=True)
    usn = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    dept = Column(String(100), nullable=True)
    semester = Column(Integer, nullable=True)


class Subject(Base):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    dept = Column(String(100), nullable=True)
    semester = Column(Integer, nullable=True)


class FacultyAssignment(Base):
    __tablename__ = 'faculty_assignment'
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    faculty = relationship('User', backref='assignments')
    subject = relationship('Subject')


class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    attended = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    student = relationship('Student', backref='attendance')
    subject = relationship('Subject')


class Marks(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    internal = Column(Float, nullable=True, default=0.0)
    external = Column(Float, nullable=True, default=0.0)
    student = relationship('Student', backref='marks')
    subject = relationship('Subject')


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username='admin').first():
            u = User(username='admin', role='Admin')
            u.set_password('adminpass')
            db.add(u)
        if not db.query(User).filter_by(username='hod').first():
            h = User(username='hod', role='HOD')
            h.set_password('hodpass')
            db.add(h)
        if not db.query(User).filter_by(username='fac1').first():
            f = User(username='fac1', role='Faculty')
            f.set_password('facpass')
            db.add(f)
        if not db.query(User).filter_by(username='1PV16CS001').first():
            suser = User(username='1PV16CS001', role='Student')
            suser.set_password('studpass')
            db.add(suser)
        if not db.query(Student).filter_by(usn='1PV16CS001').first():
            student = Student(usn='1PV16CS001', name='John Doe', dept='CSE', semester=6)
            db.add(student)
        if not db.query(Subject).filter_by(code='CS101').first():
            sub = Subject(code='CS101', name='Operating Systems', dept='CSE', semester=6)
            db.add(sub)
        if not db.query(Subject).filter_by(code='CS102').first():
            sub2 = Subject(code='CS102', name='Database Systems', dept='CSE', semester=6)
            db.add(sub2)
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session):
    user_id = request.session.get('user_id')
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


def require_role(request: Request, db: Session, roles=None):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail='Login required')
    if roles and user.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized')
    return user


def flash(request: Request, message: str, category: str = 'info'):
    request.session.setdefault('flash_messages', []).append({'msg': message, 'cat': category})


def consume_flash(request: Request):
    messages = request.session.pop('flash_messages', [])
    return messages


@app.on_event('startup')
def on_startup():
    init_db()


@app.get('/', response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url='/dashboard')
    return RedirectResponse(url='/login')

@app.get('/login', response_class=HTMLResponse)
def login_get(request: Request, db: Session = Depends(get_db)):
    ctx = {'request': request, 'user': get_current_user(request, db), 'messages': consume_flash(request)}
    return render_template_safe('login.html', request, ctx)


@app.post('/login')
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user and user.check_password(password):
        request.session['user_id'] = user.id
        return RedirectResponse('/dashboard', status_code=status.HTTP_303_SEE_OTHER)
    flash(request, 'Invalid credentials', 'danger')
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db)
    if user.role == 'Admin':
        template = 'dashboard_admin.html'
    elif user.role == 'HOD':
        template = 'dashboard_hod.html'
    elif user.role == 'Faculty':
        template = 'dashboard_faculty.html'
    else:
        template = 'dashboard_student.html'
    ctx = {'request': request, 'user': user, 'messages': consume_flash(request)}
    return render_template_safe(template, request, ctx)


@app.get('/faculty/enter', response_class=HTMLResponse)
def faculty_enter(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    assigned = [a.subject for a in db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all()]
    students = db.query(Student).all()
    marks = db.query(Marks).all()
    attendance = db.query(Attendance).all()
    ctx = {
        'request': request,
        'user': user,
        'subjects': assigned,
        'students': students,
        'marks': marks,
        'attendance': attendance,
        'messages': consume_flash(request),
    }
    return render_template_safe('faculty_enter.html', request, ctx)


@app.post('/faculty/enter/marks')
def faculty_enter_marks(request: Request, student: int = Form(...), subject: int = Form(...), internal: float = Form(0.0), external: float = Form(0.0), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    marks_row = db.query(Marks).filter(Marks.student_id == student, Marks.subject_id == subject).first()
    if not marks_row:
        marks_row = Marks(student_id=student, subject_id=subject, internal=internal, external=external)
        db.add(marks_row)
    else:
        marks_row.internal = internal
        marks_row.external = external
    db.commit()
    flash(request, 'Marks saved successfully', 'success')
    return RedirectResponse('/faculty/enter', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/faculty/enter/attendance')
def faculty_enter_attendance(request: Request, student: int = Form(...), subject: int = Form(...), attended: int = Form(0), total: int = Form(0), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    att = db.query(Attendance).filter(Attendance.student_id == student, Attendance.subject_id == subject).first()
    if not att:
        att = Attendance(student_id=student, subject_id=subject, attended=attended, total=total)
        db.add(att)
    else:
        att.attended = attended
        att.total = total
    db.commit()
    flash(request, 'Attendance saved successfully', 'success')
    return RedirectResponse('/faculty/enter', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/student/view', response_class=HTMLResponse)
def student_view(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Student'])
    student = db.query(Student).filter(Student.usn == user.username).first()
    if not student:
        flash(request, 'Student record not found', 'warning')
        ctx = {'request': request, 'user': user, 'student': None, 'messages': consume_flash(request)}
        return render_template_safe('student_view.html', request, ctx)
    marks = db.query(Marks).filter(Marks.student_id == student.id).all()
    attendance = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    results = []
    for m in marks:
        total = (m.internal or 0) + (m.external or 0)
        results.append({'subject': m.subject.name, 'internal': m.internal, 'external': m.external, 'total': total})
    ctx = {'request': request, 'user': user, 'student': student, 'marks': results, 'attendance': attendance, 'messages': consume_flash(request)}
    return render_template_safe('student_view.html', request, ctx)


@app.get('/hod/assign', response_class=HTMLResponse)
def hod_assign(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    faculties = db.query(User).filter(User.role == 'Faculty').all()
    subjects = db.query(Subject).all()
    assignments = db.query(FacultyAssignment).all()
    ctx = {'request': request, 'user': user, 'faculties': faculties, 'subjects': subjects, 'assignments': assignments, 'messages': consume_flash(request)}
    return render_template_safe('hod_assign.html', request, ctx)


@app.post('/hod/assign')
def hod_assign_post(request: Request, faculty: int = Form(...), subject: int = Form(...), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    existing = db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == faculty, FacultyAssignment.subject_id == subject).first()
    if existing:
        flash(request, 'Assignment already exists', 'warning')
    else:
        fa = FacultyAssignment(faculty_id=faculty, subject_id=subject)
        db.add(fa)
        db.commit()
        flash(request, 'Assigned successfully', 'success')
    return RedirectResponse('/hod/assign', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin/students', response_class=HTMLResponse)
def admin_students(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    students = db.query(Student).all()
    ctx = {'request': request, 'user': user, 'students': students, 'messages': consume_flash(request)}
    return render_template_safe('admin_students.html', request, ctx)


# Admin: add / edit / delete student routes (templates expect these names)
@app.get('/admin/students/add', response_class=HTMLResponse)
def admin_add_student(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    ctx = {'request': request, 'user': user, 'messages': consume_flash(request)}
    return render_template_safe('admin_add_student.html', request, ctx)


@app.post('/admin/students/add')
def admin_add_student_post(request: Request, usn: str = Form(...), name: str = Form(...), dept: str = Form(None), semester: int = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    if db.query(Student).filter(Student.usn == usn).first():
        flash(request, 'USN already exists', 'danger')
        return RedirectResponse('/admin/students/add', status_code=status.HTTP_303_SEE_OTHER)
    s = Student(usn=usn, name=name, dept=dept, semester=semester)
    db.add(s)
    db.commit()
    flash(request, 'Student added', 'success')
    return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin/students/{sid}/edit', response_class=HTMLResponse)
def admin_edit_student(request: Request, sid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    s = db.query(Student).get(sid)
    if not s:
        flash(request, 'Student not found', 'danger')
        return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)
    ctx = {'request': request, 'user': user, 'student': s, 'messages': consume_flash(request)}
    return render_template_safe('admin_edit_student.html', request, ctx)


@app.post('/admin/students/{sid}/edit')
def admin_edit_student_post(request: Request, sid: int, name: str = Form(...), dept: str = Form(None), semester: int = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    s = db.query(Student).get(sid)
    if not s:
        flash(request, 'Student not found', 'danger')
        return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)
    s.name = name
    s.dept = dept
    s.semester = semester
    db.commit()
    flash(request, 'Student updated', 'success')
    return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/admin/students/{sid}/delete')
def admin_delete_student(request: Request, sid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    s = db.query(Student).get(sid)
    if s:
        db.delete(s)
        db.commit()
        flash(request, 'Student deleted', 'success')
    else:
        flash(request, 'Student not found', 'warning')
    return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/signup')
def signup(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form('Student'), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        flash(request, 'Username already exists', 'danger')
        return RedirectResponse('/signup', status_code=status.HTTP_303_SEE_OTHER)
    u = User(username=username, role=role)
    u.set_password(password)
    db.add(u)
    db.commit()
    flash(request, 'User created', 'success')
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/signup', response_class=HTMLResponse)
def signup_get(request: Request, db: Session = Depends(get_db)):
    ctx = {'request': request, 'user': get_current_user(request, db), 'messages': consume_flash(request)}
    return render_template_safe('signup.html', request, ctx)
