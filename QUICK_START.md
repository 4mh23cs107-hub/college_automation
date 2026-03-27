# 🎓 Quick Start Guide - College Academic Management System

## 🚀 Getting Started in 5 Minutes

### Step 1: Start the Server
```powershell
# Navigate to project directory
cd college_automation

# Run the startup script
.\RUN_SERVER.ps1
```

Wait for the message:
```
Server will be available at: http://127.0.0.1:8000
```

### Step 2: Open the Application
Click here or paste in your browser:
```
http://127.0.0.1:8000/login
```

### Step 3: Login with Demo Account

Choose a demo account based on your role:

#### Admin Login
- **Username**: `admin`
- **Password**: `adminpass`
- **Access**: Full system control, manage students and records

#### HOD Login
- **Username**: `hod`
- **Password**: `hodpass`
- **Access**: Assign faculty, monitor department

#### Faculty Login
- **Username**: `fac1`
- **Password**: `facpass`
- **Access**: Enter marks and attendance

#### Student Login
- **Username**: `1PV16CS001`
- **Password**: `studpass`
- **Access**: View marks and attendance

---

## 📊 What Each Role Can Do

### 👨‍💼 Admin Can:
- ✅ Add new students
- ✅ Edit student information
- ✅ Delete student records
- ✅ Manage subjects
- ✅ View all academic records
- ✅ Calculate results

### 👔 HOD Can:
- ✅ Assign faculty to subjects
- ✅ View faculty workload
- ✅ Monitor student data
- ✅ Check attendance and marks
- ✅ Generate department reports
- ✅ View performance analytics

### 👨‍🏫 Faculty Can:
- ✅ Enter internal marks (0-50)
- ✅ Enter external marks (0-100)
- ✅ Record student attendance
- ✅ Update attendance records
- ✅ View assigned subjects
- ✅ Monitor student performance

### 🎓 Student Can:
- ✅ View personal attendance %
- ✅ Check marks in all subjects
- ✅ View total scores
- ✅ Monitor SGPA
- ✅ See attendance status (✅ Good / ⚠️ Warning / ❌ Low)

---

## 💡 Common Tasks

### As Admin - Add a New Student

1. Click on **Student Management** in dashboard
2. Click **+ Add New Student**
3. Fill in:
   - **USN**: e.g., `1PV20CS050`
   - **Name**: Student's full name
   - **Department**: Select from dropdown (CSE, ECE, ME, EE, CIVIL)
   - **Semester**: Select 1-8
4. Click **✅ Add Student**
5. Student will appear in student list

### As HOD - Assign Faculty to Subject

1. Click on **Assign Faculty to Subjects** in dashboard
2. Select a faculty member from dropdown
3. Select a subject from dropdown
4. Click **✅ Assign Faculty**
5. Assignment appears in current assignments list

### As Faculty - Enter Student Marks

1. Click on **Enter & Manage Marks** in dashboard
2. Select subject from dropdown
3. Select student from dropdown
4. Enter Internal Marks (0-50)
5. Enter External Marks (0-100)
6. Click **💾 Save Marks**
7. Marks appear in "Entered Marks" table

### As Faculty - Record Attendance

1. Click on **Mark Attendance** in dashboard
2. Select subject from dropdown
3. Select student from dropdown
4. Enter classes attended
5. Enter total classes held
6. Click **💾 Save Attendance**
7. Attendance percentage calculated automatically

### As Student - View Your Records

1. Click on **View My Attendance & Marks** in dashboard
2. See attendance for each subject with status:
   - ✅ **Green (Good)**: ≥ 75% attendance
   - ⚠️ **Yellow (Warning)**: 60-74% attendance
   - ❌ **Red (Low)**: < 60% attendance
3. See your marks:
   - Internal marks (out of 50)
   - External marks (out of 100)
   - Total marks

---

## 🔑 Important Notes

### Attendance Thresholds
- **75% or above**: ✅ Good status
- **60-74%**: ⚠️ Warning - at risk
- **Below 60%**: ❌ Low - not eligible

### Marks Format
- **Internal Marks**: 0-50 points
- **External Marks**: 0-100 points
- **Total**: Internal + External = 150 points

### Data Management
- Cannot delete users (only students through admin panel)
- Cannot edit USN after creation
- Attendance % = (Attended / Total) × 100

---

## 🆘 Troubleshooting

### Server Won't Start
```powershell
# Make sure dependencies are installed
pip install -r requirements.txt

# Check if port 8000 is free
# If not, modify:
uvicorn fastapi_app:app --port 8001
```

### Cannot Login
- ✅ Check caps lock on password
- ✅ Verify username spelling
- ✅ Try demo credentials first
- ✅ Check error message for details

### Page Not Loading
- ✅ Refresh page (Ctrl+F5)
- ✅ Check browser console (F12 > Console)
- ✅ Restart server
- ✅ Check fastapi_error.log for errors

### Database Issues
- ✅ Delete college.db to reset
- ✅ Restart server (auto-creates database)
- ✅ Demo data will be reloaded

---

## 📁 File Locations

### Configuration Files
- `fastapi_app.py` - Main application
- `requirements.txt` - Python packages
- `college.db` - SQLite database

### Templates (HTML)
- `templates/login.html` - Login page
- `templates/base.html` - Base template
- Dashboard templates: `templates/dashboard_*.html`

### Styling
- `static/css/styles.css` - Main stylesheet

### Logs
- `fastapi_error.log` - Error logs

---

## 🔐 Changing Demo Credentials

To set custom password:
1. Login as admin with `admin/adminpass`
2. Go to user management
3. Create new admin user with custom credentials
4. Delete old demo admin account

---

## 🌐 Access Points

### From Current Machine
```
http://127.0.0.1:8000/
```

### Network Access (if firewall allows)
```
http://<your-computer-ip>:8000/
```

### Pages
- Login: `http://127.0.0.1:8000/login`
- Signup: `http://127.0.0.1:8000/signup`
- Dashboard: `http://127.0.0.1:8000/dashboard`

---

## 📚 Next Steps

1. **Explore Demo Data**: Login with different roles
2. **Test Features**: Try adding students, entering marks
3. **Check Error Logs**: Review `fastapi_error.log` if issues
4. **Customize**: Add your institution details
5. **Deploy**: Move to production server if needed

---

## 💬 Need Help?

### Check These Resources
1. **README_COMPLETE.md** - Full documentation
2. **IMPLEMENTATION_CHECKLIST.md** - System features
3. **fastapi_error.log** - Error details
4. **Console (F12)** - Browser errors
5. **Terminal** - Server messages

### Common Errors
| Error | Solution |
|-------|----------|
| Port 8000 in use | Change port: `--port 8001` |
| Module not found | Run: `pip install -r requirements.txt` |
| Database locked | Restart server, delete college.db |
| Template error | Check fastapi_error.log file |
| Static files 404 | Verify static/css/styles.css exists |

---

## ✨ Features Summary

| Feature | Admin | HOD | Faculty | Student |
|---------|:-----:|:---:|:-------:|:-------:|
| Manage Students | ✅ | 🔍 | ❌ | ❌ |
| View/Enter Marks | ✅ | 🔍 | ✅ | ✅ |
| Mark Attendance | ❌ | 🔍 | ✅ | ❌ |
| Assign Faculty | ❌ | ✅ | ❌ | ❌ |
| View Dashboard | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ = Can do | 🔍 = Can view | ❌ = No access

---

## 🎯 Quick Reference

### URLs to Remember
```
login: http://127.0.0.1:8000/login
logout: Click "Logout" in header
```

### Demo Users
```
admin / adminpass (Admin)
hod / hodpass (HOD)
fac1 / facpass (Faculty)
1PV16CS001 / studpass (Student)
```

### Database
```
File: college.db
Type: SQLite 3
Auto-created on first run
```

### Logs
```
Error log: fastapi_error.log
Server logs: Terminal output
```

---

## 🚀 Ready to Go!

Your College Academic Management System is ready to use.

**Happy Managing! 🎓**

---

*For detailed information, refer to README_COMPLETE.md*
