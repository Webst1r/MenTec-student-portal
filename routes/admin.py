from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, Course, Role
from ..security import require_role

router = APIRouter(prefix="/app/admin")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/users")
def users_page(request: Request, user: User = Depends(require_role(Role.admin)),
               session: Session = Depends(get_session)):
    users = session.exec(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        "portal/admin_users.html",
        {"request": request, "user": user, "users": users, "roles": list(Role)},
    )


@router.post("/users/{user_id}/role")
def change_role(user_id: int, role: str = Form(...),
                user: User = Depends(require_role(Role.admin)),
                session: Session = Depends(get_session)):
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    try:
        target.role = Role(role)
    except ValueError:
        raise HTTPException(400, "Invalid role")
    session.add(target); session.commit()
    return RedirectResponse(url="/app/admin/users", status_code=303)


@router.get("/courses")
def admin_courses(request: Request, user: User = Depends(require_role(Role.admin)),
                  session: Session = Depends(get_session)):
    courses = session.exec(select(Course)).all()
    lecturers = session.exec(select(User).where(User.role == Role.lecturer)).all()
    return templates.TemplateResponse(
        "portal/admin_courses.html",
        {"request": request, "user": user, "courses": courses, "lecturers": lecturers},
    )


@router.post("/courses/new")
def create_course(
    code: str = Form(...), title: str = Form(...),
    description: str = Form(""), lecturer_id: int = Form(...),
    user: User = Depends(require_role(Role.admin)),
    session: Session = Depends(get_session),
):
    if session.exec(select(Course).where(Course.code == code.strip())).first():
        raise HTTPException(400, "Course code already exists")
    session.add(Course(code=code.strip(), title=title.strip(),
                       description=description.strip(), lecturer_id=lecturer_id))
    session.commit()
    return RedirectResponse(url="/app/admin/courses", status_code=303)


@router.post("/courses/{course_id}/delete")
def delete_course(course_id: int,
                  user: User = Depends(require_role(Role.admin)),
                  session: Session = Depends(get_session)):
    c = session.get(Course, course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    session.delete(c); session.commit()
    return RedirectResponse(url="/app/admin/courses", status_code=303)
