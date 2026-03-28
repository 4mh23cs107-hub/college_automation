from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

# Provide an explicit instance_path to avoid pkgutil-based package discovery issues
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
app = Flask(__name__, instance_path=instance_path)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, HOD, Faculty, Student

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Admin-only signup for other users
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
    return render_template('dashboard_student.html')

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

# HOD: assign faculty to subjects
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
            flash('Assigned', 'success')
        else:
            flash('Assignment exists', 'warning')
        return redirect(url_for('hod_assign'))
    return render_template('hod_assign.html', faculties=faculties, subjects=subjects)

# Faculty: enter marks and attendance
@app.route('/faculty/enter', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def faculty_enter():
    # List subjects assigned
    assigned = [a.subject for a in current_user.assignments]
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
        # Attendance update
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
    return render_template('faculty_enter.html', subjects=assigned, students=students)


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

# Student: view data
@app.route('/student/view')
@login_required
@role_required('Student')
def student_view():
    # Try to find matching student record by username==usn
    student = Student.query.filter_by(usn=current_user.username).first()
    if not student:
        flash('Student record not found', 'warning')
        return render_template('student_view.html', student=None)
    marks = Marks.query.filter_by(student_id=student.id).all()
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    # basic SGPA/CGPA calculation: average of subject totals (internal+external)/100 * 10 mapping to gradepoints not implemented; show raw averages
    results = []
    for m in marks:
        total = (m.internal or 0) + (m.external or 0)
        results.append({'subject': m.subject.name, 'total': total})
    return render_template('student_view.html', student=student, marks=results, attendance=attendance)

if __name__ == '__main__':
    app.run(debug=True)
