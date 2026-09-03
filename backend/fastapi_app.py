import os
import logging
import traceback
from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy import Column, Integer, String, ForeignKey, Float, func
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

# Mount static files with absolute path - point to frontend folder
backend_dir = os.path.dirname(__file__)
project_root = os.path.dirname(backend_dir)
static_dir = os.path.join(project_root, 'frontend', 'static')
app.mount('/static', StaticFiles(directory=static_dir))

# Templates directory in frontend folder
templates = Jinja2Templates(directory=os.path.join(project_root, 'frontend', 'templates'))

# basic logger to record unhandled exceptions
logger = logging.getLogger('fastapi_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'fastapi_error.log'))
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
    dept = Column(String(100), nullable=True)

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


class MarksCard(Base):
    __tablename__ = 'marks_card'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(String(50), nullable=True)
    student = relationship('Student', backref='marks_cards')


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


def get_or_create_student_profile(db: Session, user: User) -> Student:
    if not user:
        return None
    clean_usn = user.username.strip()
    student = db.query(Student).filter(Student.usn == clean_usn).first()
    if not student:
        student = db.query(Student).filter(func.lower(Student.usn) == func.lower(clean_usn)).first()
    if not student and user.role == 'Student':
        student = Student(
            usn=clean_usn,
            name=clean_usn,
            dept=user.dept or 'CSE',
            semester=1
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db)
    ctx = {'request': request, 'user': user, 'messages': consume_flash(request)}
    if user.role == 'Admin':
        template = 'dashboard_admin.html'
    elif user.role == 'HOD':
        template = 'dashboard_hod.html'
    elif user.role == 'Faculty':
        template = 'dashboard_faculty.html'
    else:
        template = 'dashboard_student.html'
        student = get_or_create_student_profile(db, user)
        attendance = db.query(Attendance).filter(Attendance.student_id == student.id).all() if student else []
        marks = db.query(Marks).filter(Marks.student_id == student.id).all() if student else []
        
        avg_attendance = 0.0
        if attendance:
            total_att = sum([a.attended for a in attendance])
            total_tot = sum([a.total for a in attendance if a.total])
            avg_attendance = round((total_att / total_tot * 100), 1) if total_tot > 0 else 0.0
            
        ctx.update({
            'student': student,
            'attendance': attendance,
            'marks': marks,
            'avg_attendance': avg_attendance,
            'enrolled_subjects_count': max(len(attendance), len(marks))
        })
    return render_template_safe(template, request, ctx)



@app.get('/faculty/enter', response_class=HTMLResponse)
def faculty_enter(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    assigned = [a.subject for a in db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all() if a.subject]
    if not assigned:
        if user.dept:
            assigned = db.query(Subject).filter(Subject.dept == user.dept).all()
        if not assigned:
            assigned = db.query(Subject).all()
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
def student_view(request: Request, type: str = None, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Student'])
    student = get_or_create_student_profile(db, user)
    
    marks = db.query(Marks).filter(Marks.student_id == student.id).all() if student else []
    attendance = db.query(Attendance).filter(Attendance.student_id == student.id).all() if student else []
    
    marks_data = []
    attendance_data = []
    sgpa = 0.0
    
    if type == 'marks':
        for m in marks:
            total = (m.internal or 0) + (m.external or 0)
            sub_name = m.subject.name if m.subject else "Subject"
            marks_data.append({'subject': sub_name, 'internal': m.internal, 'external': m.external, 'total': total})
    elif type == 'attendance':
        attendance_data = attendance
    elif type == 'sgpa':
        if marks:
            total_marks = sum([(m.internal or 0) + (m.external or 0) for m in marks])
            max_marks = len(marks) * 100
            sgpa = round((total_marks / max_marks * 10), 2) if max_marks > 0 else 0.0
    else:
        for m in marks:
            total = (m.internal or 0) + (m.external or 0)
            sub_name = m.subject.name if m.subject else "Subject"
            marks_data.append({'subject': sub_name, 'internal': m.internal, 'external': m.external, 'total': total})
        attendance_data = attendance
    
    ctx = {
        'request': request,
        'user': user,
        'student': student,
        'marks': marks_data,
        'attendance': attendance_data,
        'sgpa': sgpa,
        'messages': consume_flash(request),
        'view_type': type
    }
    return render_template_safe('student_view.html', request, ctx)



DEPARTMENTS = ['CSE', 'ISE', 'ECE', 'EEE', 'ME', 'CE', 'AI&ML', 'DS']

@app.get('/hod/assign', response_class=HTMLResponse)
def hod_assign(request: Request, dept: str = None, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    filter_dept = dept or user.dept
    faculties_query = db.query(User).filter(User.role == 'Faculty')
    subjects_query = db.query(Subject)
    if filter_dept:
        faculties = faculties_query.filter(User.dept == filter_dept).all()
        subjects = subjects_query.filter(Subject.dept == filter_dept).all()
    else:
        faculties = faculties_query.all()
        subjects = subjects_query.all()
    assignments = db.query(FacultyAssignment).all()
    ctx = {
        'request': request,
        'user': user,
        'faculties': faculties,
        'subjects': subjects,
        'assignments': assignments,
        'departments': DEPARTMENTS,
        'selected_dept': filter_dept,
        'messages': consume_flash(request)
    }
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


@app.post('/hod/subjects/add')
def hod_add_subject(request: Request, code: str = Form(...), name: str = Form(...), dept: str = Form(None), semester: int = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    existing = db.query(Subject).filter(Subject.code == code).first()
    if existing:
        flash(request, 'Subject code already exists', 'warning')
    else:
        subject = Subject(code=code, name=name, dept=dept or user.dept, semester=semester)
        db.add(subject)
        db.commit()
        flash(request, 'Subject added successfully', 'success')
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
    if user.dept:
        faculties = db.query(User).filter(User.role == 'Faculty', User.dept == user.dept).all()
    else:
        faculties = db.query(User).filter(User.role == 'Faculty').all()
    
    faculty_data = []
    for fac in faculties:
        assignments = db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == fac.id).all()
        faculty_data.append({
            'user': fac,
            'assignments': assignments,
            'num_subjects': len(assignments),
            'department': fac.dept
        })
    ctx = {'request': request, 'user': user, 'faculty_data': faculty_data, 'messages': consume_flash(request)}
    return render_template_safe('hod_view_faculty.html', request, ctx)


@app.post('/hod/faculty/add')
def hod_add_faculty(request: Request, username: str = Form(...), password: str = Form(...), dept: str = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        flash(request, 'Faculty username already exists', 'warning')
    else:
        new_fac = User(username=username, role='Faculty', dept=dept or user.dept)
        new_fac.set_password(password)
        db.add(new_fac)
        db.commit()
        flash(request, 'Faculty added successfully', 'success')
    return RedirectResponse('/hod/faculty', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/faculty/{fid}/delete')
def hod_delete_faculty(request: Request, fid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    fac = db.query(User).filter(User.id == fid, User.role == 'Faculty').first()
    if fac:
        db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == fid).delete()
        db.delete(fac)
        db.commit()
        flash(request, 'Faculty member removed successfully', 'success')
    else:
        flash(request, 'Faculty member not found', 'warning')
    return RedirectResponse('/hod/faculty', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/hod/students', response_class=HTMLResponse)
def hod_view_students(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    if user.dept:
        students = db.query(Student).filter(Student.dept == user.dept).all()
    else:
        students = db.query(Student).all()
    
    student_data = []
    for student in students:
        attendance_records = db.query(Attendance).filter(Attendance.student_id == student.id).all()
        marks_records = db.query(Marks).filter(Marks.student_id == student.id).all()
        
        avg_attendance = 0
        if attendance_records:
            total_percentage = sum([(a.attended / a.total * 100) if a.total else 0 for a in attendance_records])
            avg_attendance = total_percentage / len(attendance_records)
        
        ia_marks = []
        for mark in marks_records:
            if mark.internal is not None and mark.subject:
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
def hod_add_student(request: Request, usn: str = Form(...), name: str = Form(...), password: str = Form(...), semester: int = Form(None), dept: str = Form(None), db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    student_dept = dept or user.dept or 'CSE'
    existing_usn = db.query(Student).filter(Student.usn == usn).first()
    existing_user = db.query(User).filter(User.username == usn).first()
    if existing_usn or existing_user:
        flash(request, 'Student USN already exists', 'warning')
    else:
        u = User(username=usn, role='Student', dept=student_dept)
        u.set_password(password)
        db.add(u)
        st = Student(usn=usn, name=name, dept=student_dept, semester=semester)
        db.add(st)
        db.commit()
        flash(request, 'Student added successfully', 'success')
    return RedirectResponse('/hod/students', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/hod/students/{sid}/delete')
def hod_delete_student(request: Request, sid: int, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    st = db.query(Student).filter(Student.id == sid).first()
    if st:
        db.query(Marks).filter(Marks.student_id == sid).delete()
        db.query(Attendance).filter(Attendance.student_id == sid).delete()
        db.query(User).filter(User.username == st.usn).delete()
        db.delete(st)
        db.commit()
        flash(request, 'Student record deleted successfully', 'success')
    else:
        flash(request, 'Student not found', 'warning')
    return RedirectResponse('/hod/students', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/hod/analytics', response_class=HTMLResponse)
def hod_analytics(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['HOD'])
    dept = user.dept
    
    if dept:
        students = db.query(Student).filter(Student.dept == dept).all()
        subjects = db.query(Subject).filter(Subject.dept == dept).all()
        faculties = db.query(User).filter(User.role == 'Faculty', User.dept == dept).all()
    else:
        students = db.query(Student).all()
        subjects = db.query(Subject).all()
        faculties = db.query(User).filter(User.role == 'Faculty').all()
        
    student_ids = [s.id for s in students]
    
    attendance_records = db.query(Attendance).filter(Attendance.student_id.in_(student_ids)).all() if student_ids else []
    marks_records = db.query(Marks).filter(Marks.student_id.in_(student_ids)).all() if student_ids else []
    
    total_students = len(students)
    total_faculties = len(faculties)
    total_subjects = len(subjects)
    
    overall_attendance_pct = 0.0
    low_attendance_list = []
    
    if attendance_records:
        total_att = sum([a.attended for a in attendance_records])
        total_tot = sum([a.total for a in attendance_records if a.total])
        overall_attendance_pct = round((total_att / total_tot * 100), 1) if total_tot > 0 else 0.0
        
        for st in students:
            st_att = [a for a in attendance_records if a.student_id == st.id]
            if st_att:
                st_attended = sum([a.attended for a in st_att])
                st_total = sum([a.total for a in st_att if a.total])
                pct = round((st_attended / st_total * 100), 1) if st_total > 0 else 0
                if pct < 75:
                    low_attendance_list.append({
                        'student': st,
                        'attendance_pct': pct,
                        'attended': st_attended,
                        'total': st_total
                    })
    
    subject_analytics = []
    for sub in subjects:
        sub_marks = [m for m in marks_records if m.subject_id == sub.id]
        sub_att = [a for a in attendance_records if a.subject_id == sub.id]
        
        avg_internal = round(sum([m.internal or 0 for m in sub_marks]) / len(sub_marks), 1) if sub_marks else 0.0
        avg_external = round(sum([m.external or 0 for m in sub_marks]) / len(sub_marks), 1) if sub_marks else 0.0
        
        sub_att_tot = sum([a.total for a in sub_att if a.total])
        sub_att_done = sum([a.attended for a in sub_att])
        sub_att_pct = round((sub_att_done / sub_att_tot * 100), 1) if sub_att_tot > 0 else 0.0
        
        assignment = db.query(FacultyAssignment).filter(FacultyAssignment.subject_id == sub.id).first()
        fac_name = assignment.faculty.username if assignment and assignment.faculty else 'Unassigned'
        
        subject_analytics.append({
            'subject': sub,
            'assigned_faculty': fac_name,
            'avg_internal': avg_internal,
            'avg_external': avg_external,
            'avg_total': avg_internal + avg_external,
            'avg_attendance_pct': sub_att_pct,
            'enrolled_count': len(sub_marks) or len(sub_att) or len(students)
        })
        
    ctx = {
        'request': request,
        'user': user,
        'total_students': total_students,
        'total_faculties': total_faculties,
        'total_subjects': total_subjects,
        'overall_attendance_pct': overall_attendance_pct,
        'low_attendance_list': low_attendance_list,
        'subject_analytics': subject_analytics,
        'messages': consume_flash(request)
    }
    return render_template_safe('hod_analytics.html', request, ctx)




@app.get('/faculty/subjects', response_class=HTMLResponse)
def faculty_view_subjects(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    assignments = db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all()
    subjects = [a.subject for a in assignments]
    ctx = {'request': request, 'user': user, 'subjects': subjects, 'messages': consume_flash(request)}
    return render_template_safe('faculty_view_subjects.html', request, ctx)


@app.get('/faculty/marks', response_class=HTMLResponse)
def faculty_view_marks(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    assigned_subjects = [a.subject for a in db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all() if a.subject]
    if not assigned_subjects:
        if user.dept:
            assigned_subjects = db.query(Subject).filter(Subject.dept == user.dept).all()
        if not assigned_subjects:
            assigned_subjects = db.query(Subject).all()
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = db.query(Student).all()
    marks = db.query(Marks).filter(Marks.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    ctx = {
        'request': request,
        'user': user,
        'subjects': assigned_subjects,
        'students': students,
        'marks': marks,
        'attendance': [],
        'messages': consume_flash(request),
        'view_type': 'marks'
    }
    return render_template_safe('faculty_enter.html', request, ctx)


@app.get('/faculty/attendance', response_class=HTMLResponse)
def faculty_view_attendance(request: Request, db: Session = Depends(get_db)):
    user = require_role(request, db, roles=['Faculty'])
    assigned_subjects = [a.subject for a in db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all() if a.subject]
    if not assigned_subjects:
        if user.dept:
            assigned_subjects = db.query(Subject).filter(Subject.dept == user.dept).all()
        if not assigned_subjects:
            assigned_subjects = db.query(Subject).all()
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = db.query(Student).all()
    attendance = db.query(Attendance).filter(Attendance.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    ctx = {
        'request': request,
        'user': user,
        'subjects': assigned_subjects,
        'students': students,
        'marks': [],
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
    
    # Create marks_cards directory if it doesn't exist - use absolute path
    backend_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(backend_dir)
    markers_dir = os.path.join(project_root, 'frontend', 'static', 'marks_cards')
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
    
    student = get_or_create_student_profile(db, user)
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
    student = get_or_create_student_profile(db, user)
    marks_card = db.query(MarksCard).filter(MarksCard.student_id == student.id).first() if student else None
    ctx = {'request': request, 'user': user, 'student': student, 'marks_card': marks_card, 'messages': consume_flash(request)}
    return render_template_safe('student_marks_card.html', request, ctx)


@app.post('/signup')
def signup(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form('Student'), db: Session = Depends(get_db)):
    clean_username = username.strip()
    user = db.query(User).filter(func.lower(User.username) == func.lower(clean_username)).first()
    if user:
        flash(request, 'Username already exists', 'danger')
        return RedirectResponse('/signup', status_code=status.HTTP_303_SEE_OTHER)
    u = User(username=clean_username, role=role)
    u.set_password(password)
    db.add(u)
    
    if role == 'Student':
        st = Student(usn=clean_username, name=clean_username, dept='CSE', semester=1)
        db.add(st)
        
    db.commit()
    flash(request, 'User account created successfully! Please log in.', 'success')
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)



@app.get('/signup', response_class=HTMLResponse)
def signup_get(request: Request, db: Session = Depends(get_db)):
    ctx = {'request': request, 'user': get_current_user(request, db), 'messages': consume_flash(request)}
    return render_template_safe('signup.html', request, ctx)
