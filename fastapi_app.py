import os
from dotenv import load_dotenv

load_dotenv()
import logging
import traceback
from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import declarative_base, relationship, Session, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import shutil

# Define the engine before usage
DB_PATH = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(os.path.dirname(__file__), "college.db")}')
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if 'sqlite' in DB_PATH else {})

# Define SessionLocal before usage
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure Base is defined before usage
Base = declarative_base()

app = FastAPI(title='College Automation FastAPI')
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'dev-secret'), session_cookie='session')

# Unified templates and static directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, 'frontend', 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'frontend', 'templates'))

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
    role = Column(String(20), nullable=False)  # 'Admin', 'HOD', 'Faculty', 'Student'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    usn = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    dept = Column(String(100), nullable=True)
    semester = Column(Integer, nullable=True)
    
    user = relationship('User', backref=backref('student_profile', uselist=False))


class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    dept = Column(String(100), nullable=True)
    
    user = relationship('User', backref=backref('faculty_profile', uselist=False))


class HOD(Base):
    __tablename__ = 'hod'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    dept = Column(String(100), nullable=True)
    
    user = relationship('User', backref=backref('hod_profile', uselist=False))


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
    faculty_id = Column(Integer, ForeignKey('faculty.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    faculty = relationship('Faculty', backref='assignments')
    subject = relationship('Subject')


class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    attended = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    student = relationship('Student', backref='attendance_records')
    subject = relationship('Subject')


class Marks(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    internal = Column(Float, nullable=True, default=0.0)
    external = Column(Float, nullable=True, default=0.0)
    student = relationship('Student', backref='marks_records')
    subject = relationship('Subject')


class MarksCard(Base):
    __tablename__ = 'marks_card'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(String(50), nullable=True)
    student = relationship('Student', backref='marks_cards_records')


def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Admin
        if not db.query(User).filter_by(username='admin').first():
            u = User(username='admin', role='Admin')
            u.set_password('adminpass')
            db.add(u)
        
        # 2. HOD
        if not db.query(User).filter_by(username='hod').first():
            u_hod = User(username='hod', role='HOD')
            u_hod.set_password('hodpass')
            db.add(u_hod)
            db.flush()
            h = HOD(user_id=u_hod.id, name='HOD CSE', dept='CSE')
            db.add(h)
        
        # 3. Faculty
        if not db.query(User).filter_by(username='faculty').first():
            u_fac = User(username='faculty', role='Faculty')
            u_fac.set_password('facpass')
            db.add(u_fac)
            db.flush()
            f = Faculty(user_id=u_fac.id, name='Dr. Smith', dept='CSE')
            db.add(f)
        
        # 4. Student
        if not db.query(Student).filter_by(usn='4MH21CS001').first():
            u_stu = User(username='4MH21CS001', role='Student')
            u_stu.set_password('stupass')
            db.add(u_stu)
            db.flush()
            s = Student(user_id=u_stu.id, usn='4MH21CS001', name='John Doe', dept='CSE', semester=5)
            db.add(s)
        
        # 5. Subjects
        if not db.query(Subject).filter_by(code='CS101').first():
            s1 = Subject(code='CS101', name='Computer Networks', dept='CSE', semester=5)
            s2 = Subject(code='CS102', name='Database Systems', dept='CSE', semester=5)
            db.add_all([s1, s2])
            db.flush()
            
            # 6. Assignment
            f = db.query(Faculty).first()
            if f:
                db.add(FacultyAssignment(faculty_id=f.id, subject_id=s1.id))
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Init DB error: {e}")
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
        flash(request, 'You need to login first', 'warning')
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail='Login required', headers={"Location": "/login"})
    if roles and user.role not in roles:
        flash(request, 'You do not have permission to access this page', 'danger')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized', headers={"Location": "/dashboard"})
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
    student = user.student_profile
    if not student:
        flash(request, 'Student record not found', 'warning')
        ctx = {'request': request, 'user': user, 'student': None, 'messages': consume_flash(request)}
        return render_template_safe('student_view.html', request, ctx)
    
    marks = student.marks_records
    attendance = student.attendance_records
    results = []
    for m in marks:
        total = (m.internal or 0) + (m.external or 0)
        results.append({'subject': m.subject.name, 'internal': m.internal, 'external': m.external, 'total': total})
    
    ctx = {'request': request, 'user': user, 'student': student, 'marks': results, 'attendance': attendance, 'messages': consume_flash(request)}
    return render_template_safe('student_view.html', request, ctx)


@app.get('/hod/assign', response_class=HTMLResponse)
def hod_assign(request: Request, dept: str = None, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    # Get distinct departments for the filter dropdown
    all_depts = sorted(set(
        d[0] for d in db.query(Subject.dept).distinct().all() if d[0]
    ) | set(
        d[0] for d in db.query(Faculty.dept).distinct().all() if d[0]
    ))
    
    # Filter by department if provided
    if dept:
        faculties = db.query(Faculty).filter(Faculty.dept == dept).all()
        subjects = db.query(Subject).filter(Subject.dept == dept).all()
    else:
        faculties = db.query(Faculty).all()
        subjects = db.query(Subject).all()
    
    assignments = db.query(FacultyAssignment).all()
    ctx = {
        'request': request, 'user': user,
        'faculties': faculties, 'subjects': subjects,
        'assignments': assignments, 'departments': all_depts,
        'selected_dept': dept or '',
        'messages': consume_flash(request),
    }
    return render_template_safe('hod_assign.html', request, ctx)


@app.post('/hod/assign')
def hod_assign_post(request: Request, faculty: int = Form(...), subject: int = Form(...), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    # faculty is Faculty.id
    existing = db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == faculty, FacultyAssignment.subject_id == subject).first()
    if existing:
        flash(request, 'Assignment already exists', 'warning')
    else:
        fa = FacultyAssignment(faculty_id=faculty, subject_id=subject)
        db.add(fa)
        db.commit()
        flash(request, 'Assigned successfully', 'success')
    return RedirectResponse('/hod/assign', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/subjects/add')
async def hod_add_subject(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    form = await request.form()
    code = form.get('code', '').strip()
    name = form.get('name', '').strip()
    dept = form.get('dept', '').strip() or None
    sem_str = form.get('semester', '').strip()
    semester = int(sem_str) if sem_str else None
    if not code or not name:
        flash(request, 'Subject code and name are required', 'danger')
        return RedirectResponse('/hod/assign', status_code=status.HTTP_303_SEE_OTHER)
    if db.query(Subject).filter(Subject.code == code).first():
        flash(request, f'Subject with code "{code}" already exists', 'warning')
    else:
        sub = Subject(code=code, name=name, dept=dept, semester=semester)
        db.add(sub)
        db.commit()
        flash(request, f'Subject "{name}" ({code}) added successfully', 'success')
    return RedirectResponse('/hod/assign', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/assign/{aid}/delete')
def hod_delete_assignment(request: Request, aid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    assignment = db.query(FacultyAssignment).filter(FacultyAssignment.id == aid).first()
    if assignment:
        db.delete(assignment)
        db.commit()
        flash(request, 'Assignment removed successfully', 'success')
    else:
        flash(request, 'Assignment not found', 'warning')
    return RedirectResponse('/hod/assign', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/hod/faculty', response_class=HTMLResponse)
def hod_view_faculty(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    hod_profile = user.hod_profile
    
    # Filter faculties by department
    if hod_profile and hod_profile.dept:
        faculties = db.query(Faculty).filter(Faculty.dept == hod_profile.dept).all()
    else:
        faculties = db.query(Faculty).all()
    
    faculty_data = []
    for fac in faculties:
        assignments = fac.assignments
        faculty_data.append({
            'faculty': fac,
            'user': fac.user,
            'num_subjects': len(assignments),
            'department': fac.dept
        })
    ctx = {'request': request, 'user': user, 'faculty_data': faculty_data, 'messages': consume_flash(request)}
    return render_template_safe('hod_view_faculty.html', request, ctx)


@app.post('/hod/faculty/add')
def hod_add_faculty(request: Request, username: str = Form(...), password: str = Form(...), name: str = Form(None), dept: str = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    if db.query(User).filter(User.username == username).first():
        flash(request, f'Username "{username}" already exists', 'danger')
    else:
        new_user = User(username=username, role='Faculty')
        new_user.set_password(password)
        db.add(new_user)
        db.flush()
        
        new_fac = Faculty(user_id=new_user.id, name=name or username, dept=dept)
        db.add(new_fac)
        db.commit()
        flash(request, f'Faculty "{username}" added successfully', 'success')
    return RedirectResponse('/hod/faculty', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/faculty/{fid}/delete')
def hod_delete_faculty(request: Request, fid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    # fid is User.id in the template for now (or Faculty.id, let's stick to Faculty.id)
    fac = db.query(Faculty).filter(Faculty.id == fid).first()
    if fac:
        fac_user = fac.user
        db.delete(fac)
        if fac_user:
            db.delete(fac_user)
        db.commit()
        flash(request, 'Faculty removed successfully', 'success')
    else:
        flash(request, 'Faculty not found', 'warning')
    return RedirectResponse('/hod/faculty', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/hod/students', response_class=HTMLResponse)
def hod_view_students(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    hod_profile = user.hod_profile
    
    # Filter students by department
    if hod_profile and hod_profile.dept:
        students = db.query(Student).filter(Student.dept == hod_profile.dept).all()
    else:
        students = db.query(Student).all()
    
    # Enrich student data with attendance and marks information
    student_data = []
    for student in students:
        attendance_records = student.attendance_records
        marks_records = student.marks_records
        
        # Calculate average attendance
        avg_attendance = 0
        if attendance_records:
            total_percentage = sum([(a.attended / a.total * 100) if a.total else 0 for a in attendance_records])
            avg_attendance = total_percentage / len(attendance_records)
        
        # Get IA marks
        ia_marks = []
        for mark in marks_records:
            if mark.internal is not None:
                ia_marks.append({
                    'subject': mark.subject.name,
                    'ia_marks': mark.internal
                })
        
        student_data.append({
            'student': student,
            'avg_attendance': round(avg_attendance, 2),
            'ia_marks': ia_marks,
            'total_subjects': len(attendance_records)
        })
    
    ctx = {'request': request, 'user': user, 'student_data': student_data, 'messages': consume_flash(request)}
    return render_template_safe('hod_view_students.html', request, ctx)


@app.post('/hod/students/add')
def hod_add_student(request: Request, usn: str = Form(...), name: str = Form(...), password: str = Form(...), dept: str = Form(None), semester: int = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    # Check if USN/Username already exists
    if db.query(Student).filter(Student.usn == usn).first() or db.query(User).filter(User.username == usn).first():
        flash(request, f'USN/Username "{usn}" already exists', 'danger')
    else:
        # Create user account
        new_user = User(username=usn, role='Student')
        new_user.set_password(password)
        db.add(new_user)
        db.flush()
        
        # Create student record
        new_student = Student(user_id=new_user.id, usn=usn, name=name, dept=dept, semester=semester)
        db.add(new_student)
        db.commit()
        flash(request, f'Student "{name}" added successfully', 'success')
    return RedirectResponse('/hod/students', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/students/{sid}/delete')
def hod_delete_student(request: Request, sid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    student = db.query(Student).get(sid)
    if student:
        stu_user = student.user
        db.delete(student)
        if stu_user:
            db.delete(stu_user)
        db.commit()
        flash(request, 'Student removed successfully', 'success')
    else:
        flash(request, 'Student not found', 'warning')
    return RedirectResponse('/hod/students', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/faculty/subjects', response_class=HTMLResponse)
def faculty_view_subjects(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    fac_profile = user.faculty_profile
    if not fac_profile:
        subjects = []
    else:
        subjects = [a.subject for a in fac_profile.assignments]
    ctx = {'request': request, 'user': user, 'subjects': subjects, 'messages': consume_flash(request)}
    return render_template_safe('faculty_view_subjects.html', request, ctx)


@app.get('/faculty/marks', response_class=HTMLResponse)
def faculty_view_marks(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    fac_profile = user.faculty_profile
    if not fac_profile:
        assigned_subjects = []
    else:
        assigned_subjects = [a.subject for a in fac_profile.assignments]
        
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = db.query(Student).all()
    # Only show marks for assigned subjects
    marks = db.query(Marks).filter(Marks.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    ctx = {
        'request': request,
        'user': user,
        'subjects': assigned_subjects,
        'students': students,
        'marks': marks,
        'messages': consume_flash(request),
        'view_type': 'marks'
    }
    return render_template_safe('faculty_enter.html', request, ctx)


@app.get('/faculty/attendance', response_class=HTMLResponse)
def faculty_view_attendance(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    fac_profile = user.faculty_profile
    if not fac_profile:
        assigned_subjects = []
    else:
        assigned_subjects = [a.subject for a in fac_profile.assignments]
        
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = db.query(Student).all()
    # Only show attendance for assigned subjects
    attendance = db.query(Attendance).filter(Attendance.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    ctx = {
        'request': request,
        'user': user,
        'subjects': assigned_subjects,
        'students': students,
        'attendance': attendance,
        'messages': consume_flash(request),
        'view_type': 'attendance'
    }
    return render_template_safe('faculty_enter.html', request, ctx)


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
def admin_add_student_post(request: Request, usn: str = Form(...), name: str = Form(...), password: str = Form('student123'), dept: str = Form(None), semester: int = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    if db.query(Student).filter(Student.usn == usn).first() or db.query(User).filter(User.username == usn).first():
        flash(request, 'USN/Username already exists', 'danger')
        return RedirectResponse('/admin/students/add', status_code=status.HTTP_303_SEE_OTHER)
    
    new_user = User(username=usn, role='Student')
    new_user.set_password(password)
    db.add(new_user)
    db.flush()
    
    s = Student(user_id=new_user.id, usn=usn, name=name, dept=dept, semester=semester)
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
        stu_user = s.user
        db.delete(s)
        if stu_user:
            db.delete(stu_user)
        db.commit()
        flash(request, 'Student deleted', 'success')
    else:
        flash(request, 'Student not found', 'warning')
    return RedirectResponse('/admin/students', status_code=status.HTTP_303_SEE_OTHER)


# Admin Marks Card Management Routes
@app.get('/admin/marks-cards', response_class=HTMLResponse)
def admin_marks_cards(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    students = db.query(Student).all()
    marks_cards = db.query(MarksCard).all()
    student_cards = {}
    for card in marks_cards:
        if card.student_id not in student_cards:
            student_cards[card.student_id] = card
    ctx = {'request': request, 'user': user, 'students': students, 'student_cards': student_cards, 'messages': consume_flash(request)}
    return render_template_safe('admin_marks_cards.html', request, ctx)


@app.post('/admin/marks-cards/upload/{sid}')
async def admin_upload_marks_card(request: Request, sid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    student = db.query(Student).get(sid)
    if not student:
        flash(request, 'Student not found', 'danger')
        return RedirectResponse('/admin/marks-cards', status_code=status.HTTP_303_SEE_OTHER)
    
    # Create marks_cards directory if it doesn't exist
    markers_dir = os.path.join('static', 'marks_cards')
    os.makedirs(markers_dir, exist_ok=True)
    
    # Save the file with student USN as name
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{student.usn}_markcard{file_extension}"
    file_path = os.path.join(markers_dir, file_name)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check if student already has a marks card
        existing_card = db.query(MarksCard).filter(MarksCard.student_id == sid).first()
        if existing_card:
            # Delete old file if it exists
            if os.path.exists(existing_card.file_path):
                os.remove(existing_card.file_path)
            existing_card.file_path = file_path
            existing_card.upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            card = MarksCard(student_id=sid, file_path=file_path, upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.add(card)
        
        db.commit()
        flash(request, f'Marks card uploaded successfully for {student.name}', 'success')
    except Exception as e:
        flash(request, f'Error uploading file: {str(e)}', 'danger')
    
    return RedirectResponse('/admin/marks-cards', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/admin/marks-cards/delete/{card_id}')
def admin_delete_marks_card(request: Request, card_id: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Admin'])
    card = db.query(MarksCard).get(card_id)
    if card:
        if os.path.exists(card.file_path):
            os.remove(card.file_path)
        db.delete(card)
        db.commit()
        flash(request, 'Marks card deleted', 'success')
    else:
        flash(request, 'Marks card not found', 'warning')
    return RedirectResponse('/admin/marks-cards', status_code=status.HTTP_303_SEE_OTHER)


# Download Marks Card Route
@app.get('/student/marks-card/download/{card_id}')
def download_marks_card(request: Request, card_id: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Student'])
    card = db.query(MarksCard).get(card_id)
    if not card:
        flash(request, 'Marks card not found', 'warning')
        return RedirectResponse('/student/marks-card', status_code=status.HTTP_303_SEE_OTHER)
    
    # Verify the card belongs to the student
    student = db.query(Student).filter(Student.usn == user.username).first()
    if not student or card.student_id != student.id:
        flash(request, 'You do not have permission to download this card', 'danger')
        return RedirectResponse('/student/marks-card', status_code=status.HTTP_303_SEE_OTHER)
    
    if os.path.exists(card.file_path):
        return FileResponse(card.file_path, filename=os.path.basename(card.file_path))
    else:
        flash(request, 'File not found on server', 'warning')
        return RedirectResponse('/student/marks-card', status_code=status.HTTP_303_SEE_OTHER)


# Student Marks Card View Route
@app.get('/student/marks-card', response_class=HTMLResponse)
def student_view_marks_card(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Student'])
    student = db.query(Student).filter(Student.usn == user.username).first()
    if not student:
        flash(request, 'Student record not found', 'warning')
        ctx = {'request': request, 'user': user, 'marks_card': None, 'messages': consume_flash(request)}
        return render_template_safe('student_marks_card.html', request, ctx)
    
    marks_card = db.query(MarksCard).filter(MarksCard.student_id == student.id).first()
    ctx = {'request': request, 'user': user, 'student': student, 'marks_card': marks_card, 'messages': consume_flash(request)}
    return render_template_safe('student_marks_card.html', request, ctx)


@app.post('/signup')
def signup(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form('Student'), dept: str = Form(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        flash(request, 'Username already exists', 'danger')
        return RedirectResponse('/signup', status_code=status.HTTP_303_SEE_OTHER)
    
    u = User(username=username, role=role)
    u.set_password(password)
    db.add(u)
    db.flush()
    
    # Create profile based on role
    if role == 'Student':
        db.add(Student(user_id=u.id, usn=username, name=username, dept=dept))
    elif role == 'Faculty':
        db.add(Faculty(user_id=u.id, name=username, dept=dept))
    elif role == 'HOD':
        db.add(HOD(user_id=u.id, name=username, dept=dept))
        
    db.commit()
    flash(request, 'User created', 'success')
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/signup', response_class=HTMLResponse)
def signup_get(request: Request, db: Session = Depends(get_db)):
    ctx = {'request': request, 'user': get_current_user(request, db), 'messages': consume_flash(request)}
    return render_template_safe('signup.html', request, ctx)


# Ensure tables are created and seeded on module load
try:
    init_db()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Module-level DB init error: {e}")
