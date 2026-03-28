# Frontend Setup and Development Guide

## Overview

The frontend consists of **HTML templates**, **CSS styling**, and **JavaScript** files that are served by the FastAPI backend. The frontend is **not a separate application** - it's served from the backend server.

---

## Project Structure

```
frontend/
├── templates/              # Jinja2 HTML templates (served by backend)
│   ├── base.html          # Base template with navigation
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── dashboard_student.html
│   ├── dashboard_admin.html
│   ├── dashboard_faculty.html
│   ├── dashboard_hod.html
│   ├── admin_add_student.html
│   ├── admin_edit_student.html
│   ├── admin_students.html
│   ├── admin_marks_cards.html
│   ├── faculty_enter.html
│   ├── faculty_view_subjects.html
│   ├── hod_view_faculty.html
│   ├── hod_view_students.html
│   ├── student_view.html
│   └── student_marks_card.html
│
├── static/                # Static files served as-is
│   └── css/
│       └── styles.css    # Main stylesheet
│
├── css/                   # Additional CSS files
│   └── styles.css
│
└── js/                    # JavaScript files
    └── script.js
```

---

## Frontend Technologies

- **HTML**: Jinja2 templating engine
- **CSS**: Custom styling with responsive design
- **JavaScript**: Vanilla JavaScript for interactivity
- **HTTP**: Gets served by FastAPI backend

---

## Running Frontend

### ✅ The frontend runs automatically when the backend starts!

Simply start the backend:

```bash
cd backend
uvicorn fastapi_app:app --reload
```

Then visit: **http://localhost:8000**

---

## Frontend Development Workflow

### 1. **Edit HTML Templates**

Modify files in `frontend/templates/`:

```html
<!-- Example: frontend/templates/login.html -->
{% extends 'base.html' %}

{% block content %}
<div class="login-container">
    <!-- Your HTML here -->
</div>
{% endblock %}
```

✅ Changes reflect immediately on page refresh (with `--reload`)

### 2. **Edit CSS Styles**

Modify `frontend/static/css/styles.css`:

```css
/* Main stylesheet */
body {
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 20px;
}
```

✅ Refresh browser to see CSS changes

### 3. **Edit JavaScript**

Modify `frontend/js/script.js`:

```javascript
// JavaScript for interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Your code here
});
```

✅ Refresh browser to see JS changes

---

## Key Frontend Files

### Base Template (`base.html`)
- Navigation bar with role-based menu
- CSS/JS includes
- Extends to all other pages

### Login/Signup Pages
- User authentication forms
- Integration with backend `/login` and `/signup` routes

### Role-Based Dashboards
- **Student**: View marks card, assignments, attendance
- **Faculty**: Enter marks, manage attendance, view subjects
- **Admin**: Manage students, faculty assignments, marks cards
- **HOD**: View department faculty and students

### Template Variables

Templates receive data from backend routes as context:

```python
# Backend sends context
return templates.TemplateResponse(
    request, 
    'login.html', 
    {
        'request': request,
        'user': current_user,
        'messages': messages
    }
)
```

---

## Frontend Development Tips

### 1. **Hot Reload During Development**

Start backend with `--reload` to see changes instantly:

```bash
uvicorn fastapi_app:app --reload
```

### 2. **Using Browser Developer Tools**

Press `F12` to open DevTools:
- **Console**: Check for JavaScript errors
- **Network**: Monitor API calls
- **Elements**: Inspect HTML/CSS

### 3. **Debugging Templates**

Print variables in templates:

```html
<!-- Debug template variables -->
<pre>{{ variable }}</pre>

<!-- Check if variable exists -->
{% if variable %}
    <p>Variable exists: {{ variable }}</p>
{% else %}
    <p>Variable does not exist</p>
{% endif %}
```

### 4. **Form Submission**

Forms are handled by backend routes. Example:

```html
<!-- HTML Form -->
<form method="POST" action="/login">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <button type="submit">Login</button>
</form>
```

```python
# Backend endpoint
@app.post('/login')
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # Process login
    return RedirectResponse(...)
```

---

## CSS Customization

### Main Stylesheet Location
```
frontend/static/css/styles.css
```

### Common Customizations

**Change Color Scheme:**
```css
:root {
    --primary-color: #2196F3;  /* Blue */
    --secondary-color: #4CAF50; /* Green */
    --danger-color: #f44336;    /* Red */
}
```

**Update Button Styling:**
```css
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}
```

**Responsive Design:**
```css
@media (max-width: 768px) {
    .container {
        width: 100%;
        padding: 10px;
    }
}
```

---

## Template System (Jinja2)

### Variable Interpolation
```html
<h1>Welcome, {{ user.name }}</h1>
```

### Conditionals
```html
{% if user.role == 'Admin' %}
    <a href="/admin/dashboard">Admin Dashboard</a>
{% elif user.role == 'Faculty' %}
    <a href="/faculty/dashboard">Faculty Dashboard</a>
{% else %}
    <a href="/student/dashboard">Student Dashboard</a>
{% endif %}
```

### Loops
```html
<ul>
{% for subject in subjects %}
    <li>{{ subject.name }} ({{ subject.code }})</li>
{% endfor %}
</ul>
```

### Template Inheritance
```html
<!-- Child template extends base -->
{% extends 'base.html' %}

{% block content %}
    <!-- Page-specific content -->
{% endblock %}
```

---

## Frontend Best Practices

### 1. **Semantic HTML**
```html
<!-- ✅ Good -->
<header>Navigation</header>
<main>Content</main>
<footer>Footer</footer>

<!-- ❌ Avoid -->
<div>Navigation</div>
<div>Content</div>
```

### 2. **Accessible Forms**
```html
<!-- ✅ Good -->
<label for="username">Username:</label>
<input id="username" type="text" name="username" required>

<!-- ❌ Avoid -->
<input type="text" name="username">
```

### 3. **Responsive Design**
```html
<!-- ✅ Mobile-friendly -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### 4. **CSS Organization**
- Use CSS classes instead of inline styles
- Keep CSS in `frontend/static/css/styles.css`
- Use consistent naming conventions

---

## Common Frontend Tasks

### Add a New Page

1. Create HTML template in `frontend/templates/`:
```html
<!-- frontend/templates/new_page.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>New Page</h1>
    <!-- Your content -->
</div>
{% endblock %}
```

2. Add route in `backend/fastapi_app.py`:
```python
@app.get('/new-page')
def new_page(request: Request):
    return templates.TemplateResponse(request, 'new_page.html', {'request': request})
```

3. Add link in `frontend/templates/base.html`:
```html
<a href="/new-page">New Page</a>
```

### Add a Form

1. Create form in template:
```html
<form method="POST" action="/process-data">
    <input type="text" name="field_name" required>
    <button type="submit">Submit</button>
</form>
```

2. Handle in backend:
```python
@app.post('/process-data')
def process_data(request: Request, field_name: str = Form(...)):
    # Process data
    return RedirectResponse('/success')
```

### Add Styling

Edit `frontend/static/css/styles.css`:
```css
.new-class {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
}
```

Apply in template:
```html
<div class="new-class">Styled content</div>
```

---

## Live Editing

### Enable Auto-Reload

Backend already serves with `--reload`:
```bash
uvicorn fastapi_app:app --reload
```

### Workflow

1. **Edit file** in `frontend/` folder
2. **Save** the file (Ctrl+S)
3. **Refresh** browser (F5 or Ctrl+R)
4. **See changes immediately**

---

## Debugging Frontend Issues

### Issue: Styles not loading
```
Check:
1. frontend/static/css/styles.css exists
2. <link> tag in base.html correct
3. Browser cache (Ctrl+Shift+Del → clear cache)
```

### Issue: JavaScript errors
```
Check:
1. Open browser console (F12)
2. Look for red error messages
3. Check frontend/js/script.js
4. Check backend logs
```

### Issue: Template variables undefined
```
Check:
1. Backend sendsinformation in context
2. Template references correct variable names
3. Check fastapi_app.py route
```

---

## Frontend Files Overview

| File | Purpose |
|------|---------|
| `base.html` | Navigation, layout structure |
| `login.html` | User login form |
| `signup.html` | User registration form |
| `dashboard_*.html` | Role-specific dashboards |
| `admin_*.html` | Admin management pages |
| `faculty_*.html` | Faculty pages |
| `hod_*.html` | HOD pages |
| `student_*.html` | Student pages |
| `styles.css` | Main stylesheet |
| `script.js` | JavaScript functionality |

---

## Performance Tips

### 1. **CSS**
- Minimize CSS files
- Remove unused styles
- Use CSS variables for colors

### 2. **JavaScript**
- Load scripts at end of body
- Use vanilla JS or lightweight libraries
- Avoid global variables

### 3. **Images**
- Compress images
- Use appropriate formats (JPEG, PNG, WebP)
- Add alt text for accessibility

---

## Deployment Considerations

### Static Files
The backend serves all static files from `frontend/static/`:
```bash
GET /static/css/styles.css
GET /static/js/script.js
```

### Templates
Templates are rendered server-side by FastAPI/Jinja2, so they're not served directly.

### Production
In production, you might want to:
1. Minify CSS and JavaScript
2. Use a CDN for static files
3. Enable caching headers
4. Use a reverse proxy (Nginx) for static files

---

## Quick Reference Commands

```bash
# Start backend (frontend auto-serves)
cd backend
uvicorn fastapi_app:app --reload

# Edit frontend files
code frontend/

# View frontend in browser
http://localhost:8000

# Clear browser cache
Ctrl + Shift + Del

# Open DevTools
F12

# Hard refresh (skip cache)
Ctrl + Shift + R
```

