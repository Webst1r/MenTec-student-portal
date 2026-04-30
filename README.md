# Mentec Student Portal (FastAPI + SQLite)

A standalone Python student portal inspired by Mentec Foundation. Includes a public marketing site and an authenticated portal for students, lecturers, and admins.

## Features

- **Public site**: Home, Solutions, Track Record, About, Contact
- **Auth**: Email/password signup & login with hashed passwords (bcrypt) and signed session cookies
- **Roles**: Student, Lecturer, Admin (role-based access control)
- **Documents**: Upload, list, download, delete personal files (stored on disk under `data/uploads/`)
- **Messages**: Threaded conversations between students and lecturers
- **Courses & Grades**: Browse courses, view enrolled courses, see grades
- **Announcements**: Lecturers post; everyone reads
- **Calendar**: Personal events
- **Profile**: Update name & view role
- **Admin**: Manage users (assign roles), manage courses
- **Animated SVG favicon**: Pulsing barcode bars

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000

On first run, the SQLite database is created at `data/portal.db` and seeded with:
- Admin:    `admin@mentec.test` / `admin123`
- Lecturer: `lecturer@mentec.test` / `lecturer123`
- Student:  `student@mentec.test` / `student123`
- A sample course with the student enrolled

## Project layout

```
app/
  main.py              # FastAPI app, middleware, route registration
  config.py            # Settings (secret key, paths)
  db.py                # SQLModel engine + session
  models.py            # User, Role, Course, Enrollment, Message, Document, Announcement, CalendarEvent, Grade
  security.py          # Password hashing, session cookies, current_user, require_role
  seed.py              # Initial data
  routers/
    public.py          # /, /solutions, /track-record, /about, /contact
    auth.py            # /login, /signup, /logout
    portal.py          # /app dashboard
    documents.py       # /app/documents
    messages.py        # /app/messages
    courses.py         # /app/courses, /app/grades
    announcements.py   # /app/announcements
    calendar.py        # /app/calendar
    profile.py         # /app/profile
    admin.py           # /app/admin/users, /app/admin/courses
  templates/           # Jinja2 templates
  static/              # CSS, favicon
data/
  portal.db            # SQLite (created on first run)
  uploads/             # Uploaded documents (created on first run)
```

## Notes

- Sessions use signed cookies via `itsdangerous`. Change `SECRET_KEY` in `app/config.py` (or env var `SECRET_KEY`) before deploying.
- Uploads are restricted to 25 MB and saved with random filenames; the original name is kept in the DB.
- This is a learning/demo project — for production add CSRF protection, rate limiting, email verification, HTTPS, and a proper database.
