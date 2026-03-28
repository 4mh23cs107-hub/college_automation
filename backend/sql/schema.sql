-- PostgreSQL schema and stored procedures for Role-Based Academic Database Management System
-- Save as sql/schema.sql and run with: psql -d your_db -f sql/schema.sql

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users table (Admin, HOD, Faculty, Student)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL, -- stored as crypt(password, gen_salt('bf'))
  role VARCHAR(20) NOT NULL CHECK (role IN ('Admin','HOD','Faculty','Student')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  usn TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  dept TEXT,
  semester INT
);

-- Subjects
CREATE TABLE IF NOT EXISTS subjects (
  id SERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  dept TEXT,
  semester INT
);

-- Faculty assignments
CREATE TABLE IF NOT EXISTS faculty_assignments (
  id SERIAL PRIMARY KEY,
  faculty_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  UNIQUE(faculty_id, subject_id)
);

-- Marks (internal + external per student per subject)
CREATE TABLE IF NOT EXISTS marks (
  id SERIAL PRIMARY KEY,
  student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  internal NUMERIC DEFAULT 0,
  external NUMERIC DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(student_id, subject_id)
);

-- Attendance
CREATE TABLE IF NOT EXISTS attendance (
  id SERIAL PRIMARY KEY,
  student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
  attended INT DEFAULT 0,
  total INT DEFAULT 0,
  UNIQUE(student_id, subject_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_students_usn ON students(usn);
CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(code);

/* Stored procedures and functions */

-- Create a user (password will be hashed using bcrypt via pgcrypto)
CREATE OR REPLACE FUNCTION sp_create_user(p_username TEXT, p_password TEXT, p_role TEXT)
RETURNS INTEGER AS $$
DECLARE
  new_id INTEGER;
BEGIN
  INSERT INTO users (username, password, role)
  VALUES (p_username, crypt(p_password, gen_salt('bf')), p_role)
  RETURNING id INTO new_id;
  RETURN new_id;
EXCEPTION WHEN unique_violation THEN
  RAISE NOTICE 'Username % already exists', p_username;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Authenticate user: returns id, username, role if match
CREATE OR REPLACE FUNCTION sp_authenticate(p_username TEXT, p_password TEXT)
RETURNS TABLE(id INT, username TEXT, role TEXT) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.username, u.role
  FROM users u
  WHERE u.username = p_username
    AND u.password = crypt(p_password, u.password);
END;
$$ LANGUAGE plpgsql;

-- Student CRUD
CREATE OR REPLACE FUNCTION sp_add_student(p_usn TEXT, p_name TEXT, p_dept TEXT, p_semester INT)
RETURNS INTEGER AS $$
DECLARE
  sid INTEGER;
BEGIN
  INSERT INTO students (usn, name, dept, semester)
  VALUES (p_usn, p_name, p_dept, p_semester)
  RETURNING id INTO sid;
  RETURN sid;
EXCEPTION WHEN unique_violation THEN
  RAISE NOTICE 'USN % already exists', p_usn;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_update_student(p_id INT, p_name TEXT, p_dept TEXT, p_semester INT)
RETURNS VOID AS $$
BEGIN
  UPDATE students SET name = p_name, dept = p_dept, semester = p_semester WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_delete_student(p_id INT)
RETURNS VOID AS $$
BEGIN
  DELETE FROM students WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_get_student_by_usn(p_usn TEXT)
RETURNS TABLE(id INT, usn TEXT, name TEXT, dept TEXT, semester INT) AS $$
BEGIN
  RETURN QUERY SELECT id, usn, name, dept, semester FROM students WHERE usn = p_usn;
END;
$$ LANGUAGE plpgsql;

-- Subject CRUD
CREATE OR REPLACE FUNCTION sp_add_subject(p_code TEXT, p_name TEXT, p_dept TEXT, p_semester INT)
RETURNS INTEGER AS $$
DECLARE
  sid INTEGER;
BEGIN
  INSERT INTO subjects (code, name, dept, semester)
  VALUES (p_code, p_name, p_dept, p_semester)
  RETURNING id INTO sid;
  RETURN sid;
EXCEPTION WHEN unique_violation THEN
  RAISE NOTICE 'Subject code % already exists', p_code;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Assign faculty to subject
CREATE OR REPLACE FUNCTION sp_assign_faculty(p_faculty_username TEXT, p_subject_code TEXT)
RETURNS INTEGER AS $$
DECLARE
  fid INT;
  sid INT;
  faid INT;
BEGIN
  SELECT id INTO fid FROM users WHERE username = p_faculty_username AND role = 'Faculty';
  IF fid IS NULL THEN
    RAISE EXCEPTION 'Faculty user % not found', p_faculty_username;
  END IF;
  SELECT id INTO sid FROM subjects WHERE code = p_subject_code;
  IF sid IS NULL THEN
    RAISE EXCEPTION 'Subject % not found', p_subject_code;
  END IF;
  INSERT INTO faculty_assignments (faculty_id, subject_id)
  VALUES (fid, sid)
  RETURNING id INTO faid;
  RETURN faid;
EXCEPTION WHEN unique_violation THEN
  RAISE NOTICE 'Assignment already exists';
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Add or update marks for a student & subject
CREATE OR REPLACE FUNCTION sp_upsert_marks(p_usn TEXT, p_subject_code TEXT, p_internal NUMERIC, p_external NUMERIC)
RETURNS VOID AS $$
DECLARE
  stid INT;
  subid INT;
BEGIN
  SELECT id INTO stid FROM students WHERE usn = p_usn;
  IF stid IS NULL THEN
    RAISE EXCEPTION 'Student with USN % not found', p_usn;
  END IF;
  SELECT id INTO subid FROM subjects WHERE code = p_subject_code;
  IF subid IS NULL THEN
    RAISE EXCEPTION 'Subject % not found', p_subject_code;
  END IF;
  INSERT INTO marks (student_id, subject_id, internal, external, updated_at)
  VALUES (stid, subid, p_internal, p_external, now())
  ON CONFLICT (student_id, subject_id) DO UPDATE
    SET internal = EXCLUDED.internal, external = EXCLUDED.external, updated_at = now();
END;
$$ LANGUAGE plpgsql;

-- Add or update attendance
CREATE OR REPLACE FUNCTION sp_upsert_attendance(p_usn TEXT, p_subject_code TEXT, p_attended INT, p_total INT)
RETURNS VOID AS $$
DECLARE
  stid INT;
  subid INT;
BEGIN
  SELECT id INTO stid FROM students WHERE usn = p_usn;
  IF stid IS NULL THEN
    RAISE EXCEPTION 'Student with USN % not found', p_usn;
  END IF;
  SELECT id INTO subid FROM subjects WHERE code = p_subject_code;
  IF subid IS NULL THEN
    RAISE EXCEPTION 'Subject % not found', p_subject_code;
  END IF;
  INSERT INTO attendance (student_id, subject_id, attended, total)
  VALUES (stid, subid, p_attended, p_total)
  ON CONFLICT (student_id, subject_id) DO UPDATE
    SET attended = EXCLUDED.attended, total = EXCLUDED.total;
END;
$$ LANGUAGE plpgsql;

-- Get student's academic record (marks + attendance + calculated totals and gradepoint)
CREATE OR REPLACE FUNCTION sp_get_student_academic(p_usn TEXT)
RETURNS TABLE(subject_code TEXT, subject_name TEXT, internal NUMERIC, external NUMERIC, total NUMERIC, attended INT, total_sessions INT, attendance_percent NUMERIC, grade_point NUMERIC) AS $$
BEGIN
  RETURN QUERY
  SELECT
    sub.code,
    sub.name,
    COALESCE(m.internal,0),
    COALESCE(m.external,0),
    COALESCE(m.internal,0)+COALESCE(m.external,0) AS total,
    COALESCE(a.attended,0),
    COALESCE(a.total,0),
    CASE WHEN COALESCE(a.total,0)>0 THEN (COALESCE(a.attended,0)::NUMERIC/COALESCE(a.total,1))*100 ELSE NULL END AS attendance_percent,
    CASE WHEN (COALESCE(m.internal,0)+COALESCE(m.external,0)) IS NOT NULL THEN ((COALESCE(m.internal,0)+COALESCE(m.external,0))/100.0)*10.0 ELSE NULL END AS grade_point
  FROM students st
  LEFT JOIN marks m ON m.student_id = st.id
  LEFT JOIN subjects sub ON sub.id = m.subject_id
  LEFT JOIN attendance a ON a.student_id = st.id AND a.subject_id = sub.id
  WHERE st.usn = p_usn;
END;
$$ LANGUAGE plpgsql;

-- Calculate simple SGPA for the student (average of grade_point across subjects)
CREATE OR REPLACE FUNCTION sp_calculate_sgpa(p_usn TEXT)
RETURNS NUMERIC AS $$
DECLARE
  avg_gp NUMERIC;
BEGIN
  SELECT avg(((COALESCE(m.internal,0)+COALESCE(m.external,0))/100.0)*10.0) INTO avg_gp
  FROM students st
  JOIN marks m ON m.student_id = st.id
  WHERE st.usn = p_usn;
  RETURN ROUND(COALESCE(avg_gp,0)::NUMERIC,2);
END;
$$ LANGUAGE plpgsql;

-- View: low attendance alerts (below threshold)
CREATE OR REPLACE VIEW vw_low_attendance AS
SELECT st.usn, st.name, sub.code AS subject_code, sub.name AS subject_name,
       a.attended, a.total,
       CASE WHEN a.total>0 THEN (a.attended::NUMERIC / a.total::NUMERIC)*100 ELSE 0 END AS percent
FROM attendance a
JOIN students st ON st.id = a.student_id
JOIN subjects sub ON sub.id = a.subject_id
WHERE CASE WHEN a.total>0 THEN (a.attended::NUMERIC / a.total::NUMERIC)*100 ELSE 0 END < 75.0;

-- Utility: search students by name/usn
CREATE OR REPLACE FUNCTION sp_search_students(p_term TEXT)
RETURNS TABLE(id INT, usn TEXT, name TEXT, dept TEXT, semester INT) AS $$
BEGIN
  RETURN QUERY
  SELECT id, usn, name, dept, semester FROM students
  WHERE usn ILIKE ('%'||p_term||'%') OR name ILIKE ('%'||p_term||'%')
  ORDER BY name;
END;
$$ LANGUAGE plpgsql;

-- Grant basic permissions template (adjust roles/schemas as needed)
-- Example: GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_role;

-- End of schema.sql
