from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session, select, or_

from ..db import get_session
from ..models import User, Course, Enrollment, Announcement, Message, CalendarEvent, Role
from ..security import require_user

router = APIRouter(prefix="/app")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
@router.get("/")
def dashboard(request: Request, user: User = Depends(require_user),
              session: Session = Depends(get_session)):
    # Recent announcements
    announcements = session.exec(
        select(Announcement).order_by(Announcement.posted_at.desc()).limit(5)
    ).all()

    # Course count for the user
    if user.role == Role.student:
        courses = session.exec(
            select(Course).join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == user.id)
        ).all()
    elif user.role == Role.lecturer:
        courses = session.exec(select(Course).where(Course.lecturer_id == user.id)).all()
    else:
        courses = session.exec(select(Course)).all()

    unread = session.exec(
        select(Message).where(Message.recipient_id == user.id, Message.read == False)  # noqa: E712
    ).all()

    upcoming = session.exec(
        select(CalendarEvent).where(CalendarEvent.owner_id == user.id)
        .order_by(CalendarEvent.starts_at.asc()).limit(5)
    ).all()

    return templates.TemplateResponse(
        "portal/dashboard.html",
        {"request": request, "user": user, "announcements": announcements,
         "courses": courses, "unread_count": len(unread), "upcoming": upcoming},
    )
