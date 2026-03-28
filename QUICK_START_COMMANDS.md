# Quick Start - Essential Commands Only

## 🚀 Start the Application in 3 Steps

### Step 1: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Navigate to Backend
```bash
cd backend
```

### Step 3: Start Server
```bash
uvicorn fastapi_app:app --reload
```

✅ **Server running at:** http://localhost:8000

---

## 📝 Test Credentials

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Faculty | faculty1  | faculty123  |
| HOD     | hod1      | hod123      |
| Student | student1  | student123  |

---

## 🆘 Troubleshooting

**Server won't start?**
```powershell
pip install -r requirements.txt
```

**Port 8000 in use?**
```powershell
uvicorn fastapi_app:app --reload --port 8001
```

**Database issues?**
```powershell
Remove-Item backend/college.db
# Then restart server
```

---

## 📁 Project Structure
```
college_automation/
├── backend/          ← Python code, database
├── frontend/         ← HTML, CSS, JS
└── venv/            ← Virtual environment
```

---

## 💡 Useful Commands

- **Stop server**: `Ctrl + C`
- **Deactivate env**: `deactivate`
- **View requirements**: `cat backend/requirements.txt`
- **Check Python**: `python --version`

