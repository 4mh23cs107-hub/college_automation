# college_automation

## Login Page (Role-based)

A simple role-based login page has been added for the academic database management prototype. It includes a responsive login form, client-side validation, a role selector (Student, Faculty, HOD, Admin), and a minimal dashboard to demonstrate the flow.

Files added:
- `index.html` — login page UI
- `css/styles.css` — styles for the form and dashboard
- `js/script.js` — client-side validation and mock authentication
- `dashboard.html` — simple role-aware dashboard (demo)

To run locally:
1. Open the project folder in your file explorer.
2. Open `index.html` in your browser.

Notes:
- This is a front-end demo only; authentication is mocked client-side for demonstration.
- Integrate with your backend and secure authentication for production use.

Changes in this update:
- The login form now uses `username` + `password` only (no email).
- A role selector is shown as radio buttons (Student, Faculty, HOD, Admin).
- If the `Student` role is selected, the `username` field expects a USN-like value (alphanumeric, min 6 characters). Placeholder example: `1PV16CS001`.

## Full-stack app (Flask + PostgreSQL / SQLite fallback)

I added a minimal full-stack prototype with role-based auth and basic modules. Files added:
- `app.py` — Flask backend, models, routes, role guards
- `create_db.py` — initialize DB and seed demo users
- `requirements.txt` — Python dependencies
- `templates/` — Jinja templates for login, dashboards, and CRUD
- `static/` — CSS styles
- `.env.example` — env var template

Quick start (development with SQLite):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Initialize the DB with sample data:

```powershell
# from project root
python create_db.py
```

3. Run the app (FastAPI backend):

```powershell
uvicorn fastapi_app:app --reload
# open http://127.0.0.1:8000
```

Demo accounts created by `create_db.py`:
- Admin: `admin` / `adminpass`
- HOD: `hod` / `hodpass`
- Faculty: `fac1` / `facpass`
- Student (USN): `1PV16CS001` / `studpass`

To use PostgreSQL set `DATABASE_URL` in a `.env` file (see `.env.example`) and run `create_db.py`.

### PostgreSQL schema & procedures

I included a PostgreSQL SQL file with tables and PL/pgSQL functions to store, manage, and retrieve data:

- `sql/schema.sql` — creates tables (`users`, `students`, `subjects`, `faculty_assignments`, `marks`, `attendance`), indexes, views, and functions such as `sp_create_user`, `sp_authenticate`, `sp_add_student`, `sp_upsert_marks`, `sp_upsert_attendance`, `sp_get_student_academic`, and `sp_calculate_sgpa`.

To run the SQL file against a PostgreSQL database:

```powershell
# create database if needed, then run:
psql -h <host> -U <user> -d <db> -f sql/schema.sql
```

Example queries after loading the schema:

```sql
-- create a user (password hashed in DB)
SELECT sp_create_user('admin','adminpass','Admin');

-- add a student record
SELECT sp_add_student('1PV16CS002','Jane Doe','CSE',6);

-- upsert marks and attendance
SELECT sp_upsert_marks('1PV16CS001','CS101',25,60);
SELECT sp_upsert_attendance('1PV16CS001','CS101',18,20);

-- get student academic data
SELECT * FROM sp_get_student_academic('1PV16CS001');

-- calculate sgpa
SELECT sp_calculate_sgpa('1PV16CS001');
```

Note: The stored `sp_authenticate` uses `crypt()` to compare passwords hashed by `crypt()`/`gen_salt('bf')` (bcrypt). You can either let the DB handle hashing via `sp_create_user`, or hash on the application side and store hashes directly.

Automation:

- `setup_and_run.ps1` — PowerShell script that creates a virtual environment, installs dependencies, copies `.env.example` to `.env` (if missing), initializes the DB (SQLite by default), and starts the Flask app.

Important: I cannot run commands on your machine from here. I prepared `setup_and_run.ps1` so you can run one script locally to perform the full setup.
