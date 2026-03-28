# Complete Setup and Run Guide

## Prerequisites

Before you start, ensure you have:
- **Python 3.8+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed (for version control)
- **PowerShell** or **Command Prompt** (Windows terminal)

Verify installations:
```bash
python --version
git --version
```

---

## Step 1: Navigate to the Project

Open PowerShell or Command Prompt and navigate to your project directory:

```bash
cd C:\Users\poorv\OneDrive\Desktop\college_automation
```

---

## Step 2: Set Up Virtual Environment

### Option A: Using Existing Virtual Environment

If you already have a `venv` or `.venv` folder:

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

### Option B: Create a New Virtual Environment

**PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

✅ You should see `(venv)` prefix in your terminal once activated.

---

## Step 3: Install Dependencies

Navigate to the **backend** folder and install requirements:

```bash
cd backend
pip install -r requirements.txt
```

Expected packages to install:
- fastapi
- uvicorn
- sqlalchemy
- starlette
- jinja2
- werkzeug
- python-multipart
- aiofiles

Wait for installation to complete. ✅

---

## Step 4: Start the Application

### Option A: Using Uvicorn Directly

```bash
# Make sure you're in the backend folder and venv is activated
uvicorn fastapi_app:app --reload
```

### Option B: Using Python Module

```bash
python -m uvicorn fastapi_app:app --reload
```

### Option C: Using the Startup Script

**PowerShell:**
```powershell
.\RUN_SERVER.ps1
```

**Batch:**
```cmd
RUN_SERVER.bat
```

---

## Step 5: Access the Application

Once the server is running, you should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Open your web browser and go to:

```
http://localhost:8000
```

Or directly to:
- **Login**: `http://localhost:8000/login`
- **Signup**: `http://localhost:8000/signup`

---

## Test Users

Use these credentials to test the application:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin (Manage students, marks cards, subjects)

### Faculty User
- **Username**: `faculty1`
- **Password**: `faculty123`
- **Role**: Faculty (Enter marks, attendance, view subjects)

### HOD User
- **Username**: `hod1`
- **Password**: `hod123`
- **Role**: HOD (View faculty, students, attendance)

### Student User
- **Username**: `student1`
- **Password**: `student123`
- **Role**: Student (View dashboard, download marks card)

---

## Project Structure After Separation

```
college_automation/
├── backend/
│   ├── fastapi_app.py          ← Main application
│   ├── models.py               ← Database models
│   ├── db_helpers.py           ← Helper functions
│   ├── college.db              ← SQLite database
│   ├── requirements.txt        ← Dependencies
│   ├── RUN_SERVER.ps1          ← PowerShell start script
│   ├── RUN_SERVER.bat          ← Batch start script
│   └── ...other files
│
├── frontend/
│   ├── templates/              ← HTML templates
│   │   ├── login.html
│   │   ├── dashboard_student.html
│   │   ├── dashboard_admin.html
│   │   ├── dashboard_faculty.html
│   │   ├── dashboard_hod.html
│   │   └── ...other templates
│   ├── static/                 ← Static files
│   │   └── css/
│   │       └── styles.css
│   ├── css/                    ← CSS files
│   └── js/                     ← JavaScript files
│
└── venv/                       ← Virtual environment
```

---

## Common Commands Reference

### Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1          # PowerShell
venv\Scripts\activate.bat             # Command Prompt
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Install/Update Dependencies
```bash
pip install -r backend/requirements.txt
```

### Stop the Server
```bash
Ctrl + C
```

### View Running Port
```bash
# Server runs on port 8000 by default
# Change port if needed:
uvicorn fastapi_app:app --reload --port 8001
```

---

## Troubleshooting

### Issue: "Python is not installed"
**Solution**: Download and install Python from [python.org](https://www.python.org/downloads/)

### Issue: "No module named 'fastapi'"
**Solution**: Make sure virtual environment is activated and requirements installed:
```bash
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution**: Use a different port:
```bash
uvicorn fastapi_app:app --reload --port 8001
```

### Issue: "Database not found"
**Solution**: The database will be created automatically on first run. If issues persist:
```bash
# Delete the old database
rm backend/college.db
# Restart the server - it will create a new database
```

### Issue: "Static files not loading (CSS/JS broken)"
**Solution**: Ensure the project structure is correct and restart the server:
```bash
# Verify paths
Get-ChildItem backend/
Get-ChildItem frontend/
```

---

## Quick Start Command Chain

Copy and paste this entire block into PowerShell:

```powershell
# Navigate to project
cd C:\Users\poorv\OneDrive\Desktop\college_automation

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Go to backend
cd backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the server
uvicorn fastapi_app:app --reload
```

Then open: **http://localhost:8000**

---

## Running in Different Modes

### Development Mode (with Auto-Reload)
```bash
uvicorn fastapi_app:app --reload
```
✅ Best for development - code changes auto-reload

### Production Mode (Manual Restart)
```bash
uvicorn fastapi_app:app
```
✅ For production - no auto-reload

### With Custom Port
```bash
uvicorn fastapi_app:app --reload --port 5000
```
✅ Access at: http://localhost:5000

### With Custom Host
```bash
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000
```
✅ Accessible from other machines on network

---

## Environment Variables

Create a `.env` file in the project root (optional):

```env
DATABASE_URL=sqlite:///college.db
SECRET_KEY=your-secret-key-here
DEBUG=true
```

---

## Next Steps

After successfully running the application:

1. **Test each role** - Try logging in with different user credentials
2. **Explore dashboards** - See the role-specific dashboards
3. **Add data** - As admin, add students, faculty, subjects
4. **Check console logs** - Watch the terminal for debug information

---

## Useful Links

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Uvicorn Documentation**: https://www.uvicorn.org/

---

## Support

If you encounter any issues:

1. Check the `backend/fastapi_error.log` file for error details
2. Verify all dependencies are installed: `pip list`
3. Ensure the project structure is correct
4. Try deleting and recreating the virtual environment

