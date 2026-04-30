from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, Course, Enrollment, Grade, Role
from ..security import require_user

router = APIRouter(prefix="/app")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/courses")
def courses_page(request: Request, user: User = Depends(require_user),
                 session: Session = Depends(get_session)):
    all_courses = session.exec(select(Course)).all()
    enrolled_ids = {
        e.course_id for e in session.exec(
            select(Enrollment).where(Enrollment.student_id == user.id)
        ).all()
    }
    lecturers = {
        u.id: u for u in session.exec(select(User).where(User.role == Role.lecturer)).all()
    }
    return templates.TemplateResponse(
        "portal/courses.html",
        {"request": request, "user": user, "courses": all_courses,
         "enrolled_ids": enrolled_ids, "lecturers": lecturers},
    )


@router.post("/courses/{course_id}/enroll")
def enroll(course_id: int, user: User = Depends(require_user),
           session: Session = Depends(get_session)):
    if user.role != Role.student:
        raise HTTPException(403, "Only students can enroll")
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    existing = session.exec(
        select(Enrollment).where(Enrollment.student_id == user.id,
                                 Enrollment.course_id == course_id)
    ).first()
    if not existing:
        session.add(Enrollment(student_id=user.id, course_id=course_id))
        session.commit()
    return RedirectResponse(url="/app/courses", status_code=303)


@router.get("/grades")
def grades_page(request: Request, user: User = Depends(require_user),
                session: Session = Depends(get_session)):
    if user.role == Role.student:
        grades = session.exec(select(Grade).where(Grade.student_id == user.id)).all()
    else:
        grades = session.exec(select(Grade)).all()
    courses = {c.id: c for c in session.exec(select(Course)).all()}
    students = {u.id: u for u in session.exec(select(User)).all()}
    return templates.TemplateResponse(
        "portal/grades.html",
        {"request": request, "user": user, "grades": grades,
         "courses": courses, "students": students},
    )
