# Frontend Quick Reference

## 🚀 Frontend Basics

The frontend **runs on the backend server** - no separate installation needed!

```bash
# Start locally
cd backend
uvicorn fastapi_app:app --reload

# Open browser
http://localhost:8000
```

---

## 📁 Frontend Folder Structure

```
frontend/
├── templates/       ← HTML pages (Jinja2)
├── static/         ← CSS, JS, images
├── css/            ← Additional CSS
└── js/             ← JavaScript files
```

---

## ✏️ Editing Frontend Files

| File Type | Location | How Changes Apply |
|-----------|----------|-------------------|
| HTML | `frontend/templates/*.html` | Refresh browser (F5) |
| CSS | `frontend/static/css/styles.css` | Refresh browser (F5) |
| JavaScript | `frontend/js/script.js` | Refresh browser (F5) |

---

## 📝 Common Edits

### Edit Navigation
File: `frontend/templates/base.html`
```html
<a href="/page">Menu Item</a>
```

### Edit Dashboard
Files: `frontend/templates/dashboard_*.html`

### Edit Styles
File: `frontend/static/css/styles.css`
```css
.class-name {
    color: blue;
    padding: 10px;
}
```

### Edit JavaScript
File: `frontend/js/script.js`
```javascript
function myFunction() {
    console.log('Hello!');
}
```

---

## 🔗 Key Pages

| Page | File | Route |
|------|------|-------|
| Login | `login.html` | `/login` |
| Signup | `signup.html` | `/signup` |
| Student Dashboard | `dashboard_student.html` | `/student/dashboard` |
| Admin Dashboard | `dashboard_admin.html` | `/admin/dashboard` |
| Faculty Dashboard | `dashboard_faculty.html` | `/faculty/dashboard` |
| HOD Dashboard | `dashboard_hod.html` | `/hod/dashboard` |

---

## 🎨 Styling Best Practices

```css
/* Use CSS classes */
.container {
    max-width: 1200px;
    margin: 0 auto;
}

/* Color variables */
:root {
    --primary: #2196F3;
    --danger: #f44336;
}

/* Responsive design */
@media (max-width: 768px) {
    .container { width: 100%; }
}
```

---

## 📋 Forms Template

```html
<!-- In template -->
<form method="POST" action="/endpoint">
    <input type="text" name="field_name" required>
    <button type="submit">Submit</button>
</form>
```

```python
# In fastapi_app.py
@app.post('/endpoint')
def handle(request: Request, field_name: str = Form(...)):
    # Process
    return RedirectResponse('/success')
```

---

## 🐛 Debugging

### Check HTML/CSS
- Press `F12` → Elements tab
- Right-click → Inspect

### Check JavaScript Errors
- Press `F12` → Console tab
- Look for red error messages

### View Network Requests
- Press `F12` → Network tab
- Reload page

### View Server Logs
- Check terminal where backend is running
- Check `backend/fastapi_error.log`

---

## 🎭 Template Variables

Access data from backend:

```html
<!-- From context -->
<h1>{{ user.name }}</h1>
<p>{{ message }}</p>

<!-- Conditionals -->
{% if user.role == 'Admin' %}
    <a href="/admin">Admin</a>
{% endif %}

<!-- Loops -->
{% for item in items %}
    <li>{{ item.name }}</li>
{% endfor %}
```

---

## 🔄 Hot Reload Tips

1. Start backend with `--reload`:
   ```bash
   uvicorn fastapi_app:app --reload
   ```

2. Edit file in `frontend/`

3. Refresh browser (F5)

4. Changes appear instantly ✨

---

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| Styles not loading | Hard refresh: `Ctrl+Shift+R` |
| Changes not showing | Save file, refresh browser |
| Form submission fails | Check `backend/fastapi_error.log` |
| Page not found | Check URL matches route in `fastapi_app.py` |

---

## 📚 Template Examples

### Display User Info
```html
<div class="user-profile">
    <h2>{{ user.username }}</h2>
    <p>Role: {{ user.role }}</p>
</div>
```

### Create Button
```html
<a href="/page" class="btn btn-primary">Button Text</a>
```

### Show List
```html
<ul>
{% for item in items %}
    <li>{{ item.name }} - {{ item.value }}</li>
{% endfor %}
</ul>
```

### Show Messages
```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.cat }}">
            {{ message.msg }}
        </div>
    {% endfor %}
{% endif %}
```

---

## 🔗 File Paths in Templates

```html
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/script.js') }}"></script>

<!-- Internal links -->
<a href="/">Home</a>
<a href="/login">Login</a>

<!-- Using url_for -->
<a href="{{ url_for('dashboard') }}">Dashboard</a>
```

---

## 💡 Development Workflow

1. **Start server**
   ```bash
   cd backend && uvicorn fastapi_app:app --reload
   ```

2. **Open IDE** (VS Code)
   ```bash
   code frontend/
   ```

3. **Edit file** in `frontend/templates/` or `frontend/static/`

4. **Save** (Ctrl+S)

5. **Refresh browser** (F5)

6. **See changes** instantly! 🎉

---

## 🎯 Quick Commands

```bash
# View all templates
ls frontend/templates/

# View CSS files
ls frontend/static/css/

# View JS files
ls frontend/js/

# Search in templates
grep -r "search_term" frontend/templates/

# Find CSS class
grep -n ".class-name" frontend/static/css/styles.css
```

---

## 📖 Learn More

- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **HTML Guide**: https://developer.mozilla.org/en-US/docs/Web/HTML
- **CSS Guide**: https://developer.mozilla.org/en-US/docs/Web/CSS
- **JavaScript**: https://developer.mozilla.org/en-US/docs/Web/JavaScript

