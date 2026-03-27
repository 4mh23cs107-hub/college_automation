# Role-Based Academic Database Management System

A complete web application for managing college academics with role-based access control for Admin, HOD, Faculty, and Students.

## 🎯 Project Overview

This is a comprehensive full-stack web application built with:
- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Responsive JavaScript
- **Database**: SQLite (with SQLAlchemy ORM)
- **Architecture**: MVC with role-based access control

## 🔐 User Roles & Features

### 👨‍💼 **Admin Dashboard**
- **Student Management**: Add, edit, delete student records
- **Subject Management**: Create and manage academic subjects
- **Results Management**: Calculate and monitor SGPA/CGPA
- **Reports**: Generate academic reports

**Demo Credentials**: `admin` / `adminpass`

### 👔 **HOD (Head of Department) Dashboard**
- **Faculty Assignment**: Assign faculty to subjects
- **Faculty Management**: Manage faculty details and workload
- **Student Records**: Monitor student data and progress
- **Attendance & Marks**: View departmental academic data
- **Performance Analytics**: Track departmental performance
- **Department Reports**: Generate comprehensive reports

**Demo Credentials**: `hod` / `hodpass`

### 👨‍🏫 **Faculty Dashboard**
- **Enter Marks**: Input internal and external marks for assigned subjects
- **Mark Attendance**: Record and update student attendance
- **Subject Management**: View assigned subjects
- **Student Performance**: Track and analyze student progress

**Demo Credentials**: `fac1` / `facpass`

### 🎓 **Student Dashboard**
- **View Attendance**: Check attendance percentage per subject
- **View Marks**: See internal and external exam scores
- **View Results**: Check SGPA and CGPA
- **Performance Analytics**: Track individual academic progress

**Demo Credentials**: `1PV16CS001` / `studpass`

## 🗄️ Database Schema

### Tables

```sql
-- Users (Admin, HOD, Faculty, Students)
- id (PK)
- username (UNIQUE)
- password_hash
- role (Admin, HOD, Faculty, Student)

-- Students
- id (PK)
- usn (UNIQUE) - Unique Student Number
- name
- dept - Department
- semester

-- Subjects
- id (PK)
- code (UNIQUE)
- name
- dept
- semester

-- FacultyAssignment
- id (PK)
- faculty_id (FK)
- subject_id (FK)

-- Attendance
- id (PK)
- student_id (FK)
- subject_id (FK)
- attended - Classes attended
- total - Total classes

-- Marks
- id (PK)
- student_id (FK)
- subject_id (FK)
- internal - Internal marks (50)
- external - External marks (100)
```

## 📊 Features

### Core Features
✅ Secure Login & Signup System
✅ Role-Based Access Control (RBAC)
✅ Attendance Tracking & Percentage Calculation
✅ Mark Entry & Management
✅ SGPA/CGPA Calculation System
✅ Database-Driven Architecture
✅ Session Management

### User Interface Features
✅ Clean & Responsive Design
✅ Role-Specific Dashboards
✅ Form Validation
✅ Error Handling & Flash Messages
✅ Intuitive Navigation
✅ Mobile-Friendly Interface

### Security Features
✅ Password Hashing (Werkzeug)
✅ Session-Based Authentication
✅ Role-Based Authorization
✅ CSRF Protection
✅ SQL Injection Prevention (SQLAlchemy ORM)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual Environment (recommended)

### Installation

1. **Clone/Navigate to project**
```bash
cd college_automation
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Linux/Mac
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Application**
```bash
uvicorn fastapi_app:app --reload
```

5. **Access the Application**
- Open browser and visit: `http://127.0.0.1:8000/login`

## 📋 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `adminpass` |
| HOD | `hod` | `hodpass` |
| Faculty | `fac1` | `facpass` |
| Student | `1PV16CS001` | `studpass` |

## 📁 Project Structure

```
college_automation/
├── fastapi_app.py           # Main FastAPI application
├── app.py                   # Additional Flask app (legacy)
├── models.py                # Database models
├── db_helpers.py            # Database helpers
├── requirements.txt         # Python dependencies
├── college.db               # SQLite database
├── templates/               # HTML Templates
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── dashboard_admin.html
│   ├── dashboard_hod.html
│   ├── dashboard_faculty.html
│   ├── dashboard_student.html
│   ├── admin_students.html
│   ├── admin_add_student.html
│   ├── admin_edit_student.html
│   ├── faculty_enter.html
│   ├── hod_assign.html
│   └── student_view.html
├── static/                  # Static files
│   ├── css/styles.css      # Styling
│   └── js/script.js        # JavaScript
└── sql/
    └── schema.sql          # Database schema
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.135.2
- **Server**: Uvicorn 0.42.0
- **ORM**: SQLAlchemy 2.0.48
- **Database**: SQLite3
- **Security**: Werkzeug (Password Hashing)
- **Templating**: Jinja2 3.1.6

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with flexbox/grid
- **JavaScript**: DOM manipulation, form validation
- **Design**: Modern, clean, user-friendly UI

## 📊 Attendance Calculation

- **Percentage**: (Classes Attended / Total Classes) × 100
- **Status**:
  - ✅ **Good**: ≥ 75%
  - ⚠️ **Warning**: 60-74%
  - ❌ **Low**: < 60%

## 📈 Grade Calculation

- **Internal Marks**: Out of 50 points
- **External Marks**: Out of 100 points
- **Total Marks**: Internal + External = 150 points

## 🔄 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout
- `GET /signup` - Signup page
- `POST /signup` - Create account

### Dashboard
- `GET /` - Home redirect
- `GET /dashboard` - Role-based dashboard

### Admin Routes
- `GET /admin/students` - View all students
- `GET /admin/students/add` - Add student form
- `POST /admin/students/add` - Save new student
- `GET /admin/students/{sid}/edit` - Edit student form
- `POST /admin/students/{sid}/edit` - Update student
- `POST /admin/students/{sid}/delete` - Delete student

### Faculty Routes
- `GET /faculty/enter` - Faculty dashboard
- `POST /faculty/enter/marks` - Save marks
- `POST /faculty/enter/attendance` - Save attendance

### HOD Routes
- `GET /hod/assign` - Faculty assignment page
- `POST /hod/assign` - Assign faculty to subject

### Student Routes
- `GET /student/view` - View marks & attendance

## 🎨 UI/UX Features

### Responsive Design
- Mobile-first approach
- Flexible grid layouts
- Touch-friendly buttons
- Readable font sizes

### Visual Feedback
- Color-coded alerts (success, danger, warning, info)
- Hover effects on interactive elements
- Clear button states
- Form validation messages

### Accessibility
- Semantic HTML structure
- Proper label associations
- Clear navigation
- Readable color contrast

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL=sqlite:///college.db
SECRET_KEY=your-secret-key-here
```

### Database Configuration
- Default: SQLite (college.db)
- Connect String: `sqlite:///college.db`
- Auto-creates on first run

## 🐛 Error Handling

- Comprehensive exception handling
- Logging to `fastapi_error.log`
- User-friendly error messages
- Detailed traceback logging

## 🔒 Security Measures

1. **Password Security**
   - Hashed with Werkzeug
   - Never stored in plain text

2. **Session Management**
   - Secure session cookies
   - Session timeout support
   - User ID tracking

3. **Authorization**
   - Role-based access control
   - Function-level permission checks
   - Unauthorized access prevention

4. **Database**
   - SQL Injection prevention (SQLAlchemy ORM)
   - Prepared statements
   - Input validation

## 📝 Sample Data

The system includes pre-loaded sample data:
- 4 Demo users (1 per role)
- 1 Sample student
- 2 Sample subjects
- Sample marks and attendance records

## 🚀 Advanced Features (Extensible)

Could be added:
- 📊 PDF Report Generation
- 📈 Performance Analytics Dashboard
- 🤖 AI-based Student Performance Prediction
- 📧 Email Notifications
- 📱 Mobile App (React Native)
- 🔔 Real-time Alerts
- 📊 Statistical Analysis
- 🎓 Transcript Generation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Support & Contact

For questions or issues:
1. Check the documentation
2. Review error logs
3. Check database integrity
4. Verify user permissions

## 🎓 Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Jinja2: https://jinja.palletsprojects.com/
- Werkzeug: https://werkzeug.palletsprojects.com/

## ✨ Features Summary

| Feature | Admin | HOD | Faculty | Student |
|---------|-------|-----|---------|---------|
| Manage Students | ✅ | 🔍 | ❌ | ❌ |
| View Marks | ✅ | 🔍 | ✅ | ✅ |
| Enter Marks | ❌ | ❌ | ✅ | ❌ |
| Mark Attendance | ❌ | 🔍 | ✅ | ❌ |
| Assign Faculty | ❌ | ✅ | ❌ | ❌ |
| Manage Subjects | ✅ | 🔍 | ❌ | ❌ |
| View Dashboard | ✅ | ✅ | ✅ | ✅ |
| Generate Reports | ✅ | ✅ | ❌ | ❌ |

Legend: ✅ Full Access | 🔍 View Only | ❌ No Access

## 🎯 Next Steps

1. Add more subjects through Admin panel
2. Create faculty users for different departments
3. Assign faculty to subjects via HOD panel
4. Have faculty enter marks and attendance
5. Students can then view their academic records

---

**Last Updated**: March 27, 2026
**Version**: 1.0.0
**Status**: ✅ Production Ready
