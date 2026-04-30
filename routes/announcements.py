from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, Announcement, Role
from ..security import require_user

router = APIRouter(prefix="/app/announcements")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
def list_announcements(request: Request, user: User = Depends(require_user),
                       session: Session = Depends(get_session)):
    items = session.exec(select(Announcement).order_by(Announcement.posted_at.desc())).all()
    authors = {u.id: u for u in session.exec(select(User)).all()}
    return templates.TemplateResponse(
        "portal/announcements.html",
        {"request": request, "user": user, "announcements": items, "authors": authors},
    )


@router.post("/new")
def post_announcement(
    title: str = Form(...), body: str = Form(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    if user.role not in (Role.lecturer, Role.admin):
        raise HTTPException(403, "Only lecturers or admins can post announcements")
    session.add(Announcement(author_id=user.id, title=title.strip(), body=body.strip()))
    session.commit()
    return RedirectResponse(url="/app/announcements", status_code=303)
