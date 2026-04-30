from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, CalendarEvent
from ..security import require_user

router = APIRouter(prefix="/app/calendar")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
def calendar_page(request: Request, user: User = Depends(require_user),
                  session: Session = Depends(get_session)):
    events = session.exec(
        select(CalendarEvent).where(CalendarEvent.owner_id == user.id)
        .order_by(CalendarEvent.starts_at.asc())
    ).all()
    return templates.TemplateResponse(
        "portal/calendar.html",
        {"request": request, "user": user, "events": events},
    )


@router.post("/new")
def add_event(
    title: str = Form(...), description: str = Form(""),
    starts_at: str = Form(...), ends_at: str = Form(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    try:
        s_dt = datetime.fromisoformat(starts_at)
        e_dt = datetime.fromisoformat(ends_at)
    except ValueError:
        raise HTTPException(400, "Invalid datetime format")
    session.add(CalendarEvent(owner_id=user.id, title=title.strip(),
                              description=description.strip(),
                              starts_at=s_dt, ends_at=e_dt))
    session.commit()
    return RedirectResponse(url="/app/calendar", status_code=303)


@router.post("/{event_id}/delete")
def delete_event(event_id: int, user: User = Depends(require_user),
                 session: Session = Depends(get_session)):
    ev = session.get(CalendarEvent, event_id)
    if not ev or ev.owner_id != user.id:
        raise HTTPException(404, "Not found")
    session.delete(ev); session.commit()
    return RedirectResponse(url="/app/calendar", status_code=303)
