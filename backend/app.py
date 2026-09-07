from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
template_dir = os.path.join(project_root, 'frontend', 'templates')
static_dir = os.path.join(project_root, 'frontend', 'static')

instance_path = os.path.join(backend_dir, 'instance')
app = Flask(
    __name__,
    instance_path=instance_path,
    template_folder=template_dir,
    static_folder=static_dir
)

try:
    from uvicorn.middleware.wsgi import WSGIMiddleware
    asgi_app = WSGIMiddleware(app)
except ImportError:
    asgi_app = None


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    db_path = os.path.join(backend_dir, 'college.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.context_processor
def inject_user():
    return dict(user=current_user)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, HOD, Faculty, Student
    dept = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    dept = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.Integer, nullable=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    dept = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.Integer, nullable=True)

class FacultyAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    faculty = db.relationship('User', backref='assignments')
    subject = db.relationship('Subject', backref='assignments')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    attended = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    student = db.relationship('Student', backref='attendance')
    subject = db.relationship('Subject')

class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    internal = db.Column(db.Float, nullable=True, default=0.0)
    external = db.Column(db.Float, nullable=True, default=0.0)
    student = db.relationship('Student', backref='marks')
    subject = db.relationship('Subject')

class MarksCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.String(50), nullable=True)
    student = db.relationship('Student', backref='marks_cards')

# Role decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                flash('Access denied: insufficient permissions', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def calculate_grade_and_gp(score):
    """Map total percentage score to VTU Letter Grade and Grade Point (0-10)."""
    if score >= 90:
        return 'O', 10
    elif score >= 80:
        return 'A+', 9
    elif score >= 70:
        return 'A', 8
    elif score >= 60:
        return 'B+', 7
    elif score >= 50:
        return 'B', 6
    elif score >= 40:
        return 'C', 5
    else:
        return 'F', 0

def compute_student_sgpa_details(student_id):
    """Calculate SGPA, grade points, and course credits for a student."""
    marks_records = Marks.query.filter_by(student_id=student_id).all()
    if not marks_records:
        return {'sgpa': 0.0, 'total_credits': 0, 'earned_credits': 0, 'details': []}
    
    total_credit_points = 0
    total_credits = 0
    earned_credits = 0
    details = []
    
    for m in marks_records:
        internal = m.internal or 0.0
        external = m.external or 0.0
        total_score = internal + external
        grade, gp = calculate_grade_and_gp(total_score)
        credits = 4  # Standard course credit
        
        credit_points = gp * credits
        total_credits += credits
        total_credit_points += credit_points
        if gp > 0:
            earned_credits += credits
            
        details.append({
            'subject_code': m.subject.code if m.subject else 'N/A',
            'subject_name': m.subject.name if m.subject else 'Subject',
            'internal': internal,
            'external': external,
            'total': total_score,
            'grade': grade,
            'gp': gp,
            'credits': credits,
            'credit_points': credit_points
        })
        
    sgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
    return {
        'sgpa': sgpa,
        'total_credits': total_credits,
        'earned_credits': earned_credits,
        'details': details
    }

# Ensure database tables exist
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/reset-password', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'HOD')
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')
        target = User.query.filter_by(username=username).first()

        if not target:
            flash('No account was found for that username', 'danger')
        elif current_user.role == 'HOD' and (
            target.role not in ('Faculty', 'Student') or target.dept != current_user.dept
        ):
            flash('You can only reset passwords for users in your department', 'danger')
        elif len(password) < 8:
            flash('Password must contain at least 8 characters', 'danger')
        elif password != confirmation:
            flash('Passwords do not match', 'danger')
        else:
            target.set_password(password)
            db.session.commit()
            flash(f'Password reset successfully for {target.username}', 'success')
            return redirect(url_for('dashboard'))

    return render_template('reset_password.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'Student')
        if User.query.filter_by(username=username).first():
            flash('Username exists', 'danger')
        else:
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash('User created', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role
    if role == 'Admin':
        return render_template('dashboard_admin.html')
    if role == 'HOD':
        return render_template('dashboard_hod.html')
    if role == 'Faculty':
        return render_template('dashboard_faculty.html')
    
    student = Student.query.filter_by(usn=current_user.username).first()
    avg_attendance = None
    enrolled_subjects_count = 0
    sgpa_info = None
    if student:
        att_records = Attendance.query.filter_by(student_id=student.id).all()
        if att_records:
            tot_att = sum(a.attended for a in att_records)
            tot_tot = sum(a.total for a in att_records)
            if tot_tot > 0:
                avg_attendance = round((tot_att / tot_tot) * 100, 1)
        enrolled_subjects_count = len(att_records) or Marks.query.filter_by(student_id=student.id).count()
        sgpa_info = compute_student_sgpa_details(student.id)
    return render_template('dashboard_student.html', student=student, avg_attendance=avg_attendance, enrolled_subjects_count=enrolled_subjects_count, sgpa_info=sgpa_info)

# Admin: manage students
@app.route('/admin/students')
@login_required
@role_required('Admin')
def admin_students():
    students = Student.query.all()
    return render_template('admin_students.html', students=students)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def admin_add_student():
    if request.method == 'POST':
        usn = request.form.get('usn')
        name = request.form.get('name')
        dept = request.form.get('dept')
        semester = request.form.get('semester')
        if Student.query.filter_by(usn=usn).first():
            flash('USN already exists', 'danger')
        else:
            s = Student(usn=usn, name=name, dept=dept, semester=int(semester) if semester else None)
            db.session.add(s)
            db.session.commit()
            flash('Student added', 'success')
            return redirect(url_for('admin_students'))
    return render_template('admin_add_student.html')

@app.route('/admin/students/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def admin_edit_student(sid):
    s = Student.query.get_or_404(sid)
    if request.method == 'POST':
        s.name = request.form.get('name')
        s.dept = request.form.get('dept')
        s.semester = int(request.form.get('semester'))
        db.session.commit()
        flash('Student updated', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin_edit_student.html', student=s)

@app.route('/admin/students/<int:sid>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def admin_delete_student(sid):
    s = Student.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    flash('Student deleted', 'success')
    return redirect(url_for('admin_students'))

# Admin: Marks Cards Management
@app.route('/admin/marks-cards')
@login_required
@role_required('Admin')
def admin_marks_cards():
    students = Student.query.all()
    marks_cards = MarksCard.query.all()
    student_cards = {card.student_id: card for card in marks_cards}
    return render_template('admin_marks_cards.html', students=students, student_cards=student_cards)

@app.route('/admin/marks-cards/upload/<int:sid>', methods=['POST'])
@login_required
@role_required('Admin')
def admin_upload_marks_card(sid):
    student = Student.query.get_or_404(sid)
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin_marks_cards'))
    
    marks_dir = os.path.join(static_dir, 'marks_cards')
    os.makedirs(marks_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(f"{student.usn}_markcard{ext}")
    file_path = os.path.join(marks_dir, filename)
    file.save(file_path)
    
    existing_card = MarksCard.query.filter_by(student_id=sid).first()
    if existing_card:
        existing_card.file_path = file_path
        existing_card.upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        card = MarksCard(student_id=sid, file_path=file_path, upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(card)
    
    db.session.commit()
    flash(f'Marks card uploaded successfully for {student.name}', 'success')
    return redirect(url_for('admin_marks_cards'))

@app.route('/admin/marks-cards/delete/<int:card_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def admin_delete_marks_card(card_id):
    card = MarksCard.query.get_or_404(card_id)
    if os.path.exists(card.file_path):
        try:
            os.remove(card.file_path)
        except Exception:
            pass
    db.session.delete(card)
    db.session.commit()
    flash('Marks card deleted', 'success')
    return redirect(url_for('admin_marks_cards'))

# HOD: assign faculty to subjects & manage department
@app.route('/hod/assign', methods=['GET', 'POST'])
@login_required
@role_required('HOD')
def hod_assign():
    faculties = User.query.filter_by(role='Faculty').all()
    subjects = Subject.query.all()
    if request.method == 'POST':
        faculty_id = int(request.form.get('faculty'))
        subject_id = int(request.form.get('subject'))
        if not FacultyAssignment.query.filter_by(faculty_id=faculty_id, subject_id=subject_id).first():
            fa = FacultyAssignment(faculty_id=faculty_id, subject_id=subject_id)
            db.session.add(fa)
            db.session.commit()
            flash('Assigned successfully', 'success')
        else:
            flash('Assignment already exists', 'warning')
        return redirect(url_for('hod_assign'))
    return render_template('hod_assign.html', faculties=faculties, subjects=subjects)

@app.route('/hod/assign/<int:aid>/delete', methods=['POST'])
@login_required
@role_required('HOD')
def hod_delete_assignment(aid):
    assignment = FacultyAssignment.query.get_or_404(aid)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment removed successfully', 'success')
    return redirect(url_for('hod_assign'))

@app.route('/hod/subjects/add', methods=['POST'])
@login_required
@role_required('HOD')
def hod_add_subject():
    code = request.form.get('code')
    name = request.form.get('name')
    dept = request.form.get('dept')
    semester = request.form.get('semester')
    if not code or not name:
        flash('Subject code and name are required', 'danger')
    elif Subject.query.filter_by(code=code).first():
        flash('Subject code already exists', 'warning')
    else:
        sub = Subject(code=code, name=name, dept=dept, semester=int(semester) if semester else None)
        db.session.add(sub)
        db.session.commit()
        flash('Subject added successfully', 'success')
    return redirect(url_for('hod_assign'))

@app.route('/hod/faculty')
@login_required
@role_required('HOD')
def hod_view_faculty():
    dept = current_user.dept
    if dept:
        faculties = User.query.filter_by(role='Faculty', dept=dept).all()
    else:
        faculties = User.query.filter_by(role='Faculty').all()
    
    faculty_data = []
    for fac in faculties:
        assignments = FacultyAssignment.query.filter_by(faculty_id=fac.id).all()
        faculty_data.append({
            'user': fac,
            'assignments': assignments,
            'num_subjects': len(assignments),
            'department': fac.dept
        })
    return render_template('hod_view_faculty.html', faculty_data=faculty_data)

@app.route('/hod/faculty/add', methods=['POST'])
@login_required
@role_required('HOD')
def hod_add_faculty():
    username = request.form.get('username')
    password = request.form.get('password')
    dept = request.form.get('dept') or current_user.dept
    if User.query.filter_by(username=username).first():
        flash('Faculty username already exists', 'warning')
    else:
        new_fac = User(username=username, role='Faculty', dept=dept)
        new_fac.set_password(password)
        db.session.add(new_fac)
        db.session.commit()
        flash('Faculty member added successfully', 'success')
    return redirect(url_for('hod_view_faculty'))

@app.route('/hod/faculty/<int:fid>/delete', methods=['POST'])
@login_required
@role_required('HOD')
def hod_delete_faculty(fid):
    fac = User.query.filter_by(id=fid, role='Faculty').first_or_404()
    FacultyAssignment.query.filter_by(faculty_id=fid).delete()
    db.session.delete(fac)
    db.session.commit()
    flash('Faculty member removed successfully', 'success')
    return redirect(url_for('hod_view_faculty'))

@app.route('/hod/students')
@login_required
@role_required('HOD')
def hod_view_students():
    dept = current_user.dept
    if dept:
        students = Student.query.filter_by(dept=dept).all()
    else:
        students = Student.query.all()
    
    student_data = []
    for st in students:
        attendance_records = Attendance.query.filter_by(student_id=st.id).all()
        marks_records = Marks.query.filter_by(student_id=st.id).all()
        
        avg_att = 0.0
        if attendance_records:
            tot_pct = sum((a.attended / a.total * 100) if a.total else 0 for a in attendance_records)
            avg_att = tot_pct / len(attendance_records)
            
        ia_marks = [{'subject': m.subject.name, 'ia_marks': m.internal} for m in marks_records if m.internal is not None and m.subject]
        
        student_data.append({
            'student': st,
            'avg_attendance': round(avg_att, 2),
            'ia_marks': ia_marks,
            'total_subjects': len(attendance_records)
        })
    return render_template('hod_view_students.html', student_data=student_data)

@app.route('/hod/students/add', methods=['POST'])
@login_required
@role_required('HOD')
def hod_add_student():
    usn = request.form.get('usn')
    name = request.form.get('name')
    password = request.form.get('password')
    semester = request.form.get('semester')
    dept = request.form.get('dept') or current_user.dept or 'CSE'
    
    if Student.query.filter_by(usn=usn).first() or User.query.filter_by(username=usn).first():
        flash('Student USN already exists', 'warning')
    else:
        u = User(username=usn, role='Student', dept=dept)
        u.set_password(password)
        db.session.add(u)
        st = Student(usn=usn, name=name, dept=dept, semester=int(semester) if semester else None)
        db.session.add(st)
        db.session.commit()
        flash('Student added successfully', 'success')
    return redirect(url_for('hod_view_students'))

@app.route('/hod/students/<int:sid>/delete', methods=['POST'])
@login_required
@role_required('HOD')
def hod_delete_student(sid):
    st = Student.query.get_or_404(sid)
    Marks.query.filter_by(student_id=sid).delete()
    Attendance.query.filter_by(student_id=sid).delete()
    User.query.filter_by(username=st.usn).delete()
    db.session.delete(st)
    db.session.commit()
    flash('Student record deleted successfully', 'success')
    return redirect(url_for('hod_view_students'))

@app.route('/hod/analytics')
@login_required
@role_required('HOD')
def hod_analytics():
    dept = current_user.dept
    if dept:
        students = Student.query.filter_by(dept=dept).all()
        subjects = Subject.query.filter_by(dept=dept).all()
        faculties = User.query.filter_by(role='Faculty', dept=dept).all()
    else:
        students = Student.query.all()
        subjects = Subject.query.all()
        faculties = User.query.filter_by(role='Faculty').all()
        
    student_ids = [s.id for s in students]
    attendance_records = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all() if student_ids else []
    marks_records = Marks.query.filter(Marks.student_id.in_(student_ids)).all() if student_ids else []
    
    total_students = len(students)
    total_faculties = len(faculties)
    total_subjects = len(subjects)
    
    overall_attendance_pct = 0.0
    low_attendance_list = []
    
    if attendance_records:
        total_att = sum(a.attended for a in attendance_records)
        total_tot = sum(a.total for a in attendance_records if a.total)
        overall_attendance_pct = round((total_att / total_tot * 100), 1) if total_tot > 0 else 0.0
        
        for st in students:
            st_att = [a for a in attendance_records if a.student_id == st.id]
            if st_att:
                st_attended = sum(a.attended for a in st_att)
                st_total = sum(a.total for a in st_att if a.total)
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
        
        avg_internal = round(sum(m.internal or 0 for m in sub_marks) / len(sub_marks), 1) if sub_marks else 0.0
        avg_external = round(sum(m.external or 0 for m in sub_marks) / len(sub_marks), 1) if sub_marks else 0.0
        
        sub_att_tot = sum(a.total for a in sub_att if a.total)
        sub_att_done = sum(a.attended for a in sub_att)
        sub_att_pct = round((sub_att_done / sub_att_tot * 100), 1) if sub_att_tot > 0 else 0.0
        
        assignment = FacultyAssignment.query.filter_by(subject_id=sub.id).first()
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
        
    return render_template(
        'hod_analytics.html',
        total_students=total_students,
        total_faculties=total_faculties,
        total_subjects=total_subjects,
        overall_attendance_pct=overall_attendance_pct,
        low_attendance_list=low_attendance_list,
        subject_analytics=subject_analytics
    )

# Faculty: enter marks, attendance, view assigned subjects
@app.route('/faculty/subjects')
@login_required
@role_required('Faculty')
def faculty_view_subjects():
    assignments = FacultyAssignment.query.filter_by(faculty_id=current_user.id).all()
    subjects = [a.subject for a in assignments if a.subject]
    return render_template('faculty_view_subjects.html', subjects=subjects)

@app.route('/faculty/marks')
@login_required
@role_required('Faculty')
def faculty_view_marks():
    assigned_subjects = [a.subject for a in FacultyAssignment.query.filter_by(faculty_id=current_user.id).all() if a.subject]
    if not assigned_subjects:
        if current_user.dept:
            assigned_subjects = Subject.query.filter_by(dept=current_user.dept).all()
        if not assigned_subjects:
            assigned_subjects = Subject.query.all()
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = Student.query.all()
    marks = Marks.query.filter(Marks.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    return render_template('faculty_enter.html', subjects=assigned_subjects, students=students, marks=marks, attendance=[], view_type='marks')

@app.route('/faculty/attendance')
@login_required
@role_required('Faculty')
def faculty_view_attendance():
    assigned_subjects = [a.subject for a in FacultyAssignment.query.filter_by(faculty_id=current_user.id).all() if a.subject]
    if not assigned_subjects:
        if current_user.dept:
            assigned_subjects = Subject.query.filter_by(dept=current_user.dept).all()
        if not assigned_subjects:
            assigned_subjects = Subject.query.all()
    assigned_subject_ids = [s.id for s in assigned_subjects]
    students = Student.query.all()
    attendance = Attendance.query.filter(Attendance.subject_id.in_(assigned_subject_ids)).all() if assigned_subject_ids else []
    return render_template('faculty_enter.html', subjects=assigned_subjects, students=students, marks=[], attendance=attendance, view_type='attendance')

@app.route('/faculty/enter', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def faculty_enter():
    assigned = [a.subject for a in current_user.assignments if a.subject]
    students = Student.query.all()
    if request.method == 'POST':
        student_id = int(request.form.get('student'))
        subject_id = int(request.form.get('subject'))
        internal = float(request.form.get('internal') or 0)
        external = float(request.form.get('external') or 0)
        marks = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if not marks:
            marks = Marks(student_id=student_id, subject_id=subject_id, internal=internal, external=external)
            db.session.add(marks)
        else:
            marks.internal = internal
            marks.external = external
        
        attended = int(request.form.get('attended') or 0)
        total = int(request.form.get('total') or 0)
        att = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if not att:
            att = Attendance(student_id=student_id, subject_id=subject_id, attended=attended, total=total)
            db.session.add(att)
        else:
            att.attended = attended
            att.total = total
            
        db.session.commit()
        flash('Updated marks and attendance', 'success')
        return redirect(url_for('faculty_enter'))
    return render_template('faculty_enter.html', subjects=assigned, students=students, marks=[], attendance=[], view_type='both')

@app.route('/faculty/enter/marks', methods=['POST'])
@login_required
@role_required('Faculty')
def faculty_post_marks():
    student_id = int(request.form.get('student_id'))
    subject_id = int(request.form.get('subject_id'))
    internal = float(request.form.get('internal') or 0)
    external = float(request.form.get('external') or 0)
    
    marks = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if not marks:
        marks = Marks(student_id=student_id, subject_id=subject_id, internal=internal, external=external)
        db.session.add(marks)
    else:
        marks.internal = internal
        marks.external = external
    db.session.commit()
    flash('Marks updated successfully', 'success')
    return redirect(url_for('faculty_view_marks'))

@app.route('/faculty/enter/attendance', methods=['POST'])
@login_required
@role_required('Faculty')
def faculty_post_attendance():
    student_id = int(request.form.get('student_id'))
    subject_id = int(request.form.get('subject_id'))
    attended = int(request.form.get('attended') or 0)
    total = int(request.form.get('total') or 0)
    
    att = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if not att:
        att = Attendance(student_id=student_id, subject_id=subject_id, attended=attended, total=total)
        db.session.add(att)
    else:
        att.attended = attended
        att.total = total
    db.session.commit()
    flash('Attendance updated successfully', 'success')
    return redirect(url_for('faculty_view_attendance'))

@app.route('/faculty/subjects/add', methods=['GET', 'POST'])
@login_required
@role_required('Faculty', 'HOD', 'Admin')
def faculty_add_subject():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        dept = request.form.get('dept')
        semester = request.form.get('semester')
        if not code or not name:
            flash('Subject code and name are required', 'danger')
        elif Subject.query.filter_by(code=code).first():
            flash('Subject code already exists', 'warning')
        else:
            sub = Subject(code=code, name=name, dept=dept, semester=int(semester) if semester else None)
            db.session.add(sub)
            db.session.commit()
            flash('Subject added', 'success')
            return redirect(url_for('faculty_enter'))
    return render_template('faculty_add_subject.html')

# Student: view data & marks card
@app.route('/student/view')
@login_required
@role_required('Student')
def student_view():
    student = Student.query.filter_by(usn=current_user.username).first()
    if not student:
        flash('Student record not found', 'warning')
        return render_template('student_view.html', student=None, sgpa_info=None)
    marks = Marks.query.filter_by(student_id=student.id).all()
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    sgpa_info = compute_student_sgpa_details(student.id)
    
    results = []
    for m in marks:
        total = (m.internal or 0) + (m.external or 0)
        grade, gp = calculate_grade_and_gp(total)
        results.append({
            'subject': m.subject.name if m.subject else 'Subject',
            'code': m.subject.code if m.subject else 'N/A',
            'internal': m.internal or 0,
            'external': m.external or 0,
            'total': total,
            'grade': grade,
            'gp': gp
        })
    return render_template('student_view.html', student=student, marks=results, attendance=attendance, sgpa_info=sgpa_info)

@app.route('/student/marks-card')
@login_required
@role_required('Student')
def student_view_marks_card():
    student = Student.query.filter_by(usn=current_user.username).first()
    if not student:
        flash('Student record not found', 'warning')
        return render_template('student_marks_card.html', student=None, marks_card=None)
    marks_card = MarksCard.query.filter_by(student_id=student.id).first()
    return render_template('student_marks_card.html', student=student, marks_card=marks_card)

@app.route('/student/marks-card/download/<int:card_id>')
@login_required
@role_required('Student')
def download_marks_card(card_id):
    card = MarksCard.query.get_or_404(card_id)
    student = Student.query.filter_by(usn=current_user.username).first()
    if not student or card.student_id != student.id:
        flash('You do not have permission to download this card', 'danger')
        return redirect(url_for('student_view_marks_card'))
    
    if os.path.exists(card.file_path):
        return send_file(card.file_path, as_attachment=True)
    flash('File not found on server', 'warning')
    return redirect(url_for('student_view_marks_card'))

if __name__ == '__main__':
    app.run(debug=True)
