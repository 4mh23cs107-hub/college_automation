# Project Structure

The project has been reorganized into **backend** and **frontend** folders.

## Folder Organization

```
college_automation/
├── backend/                    # All Python/FastAPI code
│   ├── fastapi_app.py         # Main FastAPI application
│   ├── models.py              # Database models
│   ├── db_helpers.py          # Database helper functions
│   ├── create_db.py           # Database initialization
│   ├── app.py                 # Additional app logic
│   ├── college.db             # SQLite database
│   ├── requirements.txt       # Python dependencies
│   ├── instance/              # Instance-specific files
│   ├── sql/                   # SQL schema files
│   ├── RUN_SERVER.bat         # Windows server startup script
│   ├── RUN_SERVER.ps1         # PowerShell server startup script
│   ├── setup_and_run.ps1      # Setup and run script
│   └── fastapi_error.log      # Error logs
│
├── frontend/                   # All HTML/CSS/JS code
│   ├── templates/             # Jinja2 HTML templates
│   ├── static/                # Static assets
│   ├── css/                   # CSS stylesheets
│   ├── js/                    # JavaScript files
│   ├── index.html             # Main page
│   └── dashboard.html         # Dashboard page
│
├── .env                       # Environment variables
├── .env.example              # Example environment file
├── README.md                 # Project documentation
└── QUICK_START.md           # Quick start guide
```

## Running the Application

### From Backend Folder

```bash
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the server
python -m uvicorn fastapi_app:app --reload
# OR
uvicorn fastapi_app:app --reload
```

### Using Startup Scripts

From the `backend/` folder:

**Windows Batch:**
```bash
RUN_SERVER.bat
```

**PowerShell:**
```powershell
.\RUN_SERVER.ps1
# or
.\setup_and_run.ps1
```

## Key Changes

1. **Static Files Path**: FastAPI now serves static files from `frontend/static/`
2. **Templates Path**: Jinja2 templates are now loaded from `frontend/templates/`
3. **Database Path**: SQLite database (`college.db`) is stored in `backend/`
4. **Error Logs**: Logs are written to `backend/fastapi_error.log`

## Environment Variables

Place these in `.env` file (at project root):

```
DATABASE_URL=sqlite:///college.db
SECRET_KEY=your-secret-key
```

## Development Workflow

1. **Backend Developers**: Work in the `backend/` folder
   - Modify Python files, models, routes
   - Run FastAPI server from here

2. **Frontend Developers**: Work in the `frontend/` folder
   - Modify HTML templates, CSS, JavaScript
   - No need to change these files often during API changes

## Important Notes

- The `fastapi_app.py` automatically locates the `frontend/` folder
- Both `backend/` and `frontend/` are at the same level
- The `.venv/` or `venv/` environment should be in the project root or backend folder
- Make sure the database path in environment variables points to the correct location

