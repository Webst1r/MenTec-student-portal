import uuid
from pathlib import Path
from collections import defaultdict
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_, and_

from ..db import get_session
from ..models import User, Message, Role
from ..security import require_user

router = APIRouter(prefix="/app/messages")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
def inbox(request: Request, user: User = Depends(require_user),
          session: Session = Depends(get_session)):
    msgs = session.exec(
        select(Message).where(
            or_(Message.sender_id == user.id, Message.recipient_id == user.id)
        ).order_by(Message.sent_at.desc())
    ).all()

    threads = {}
    for m in msgs:
        if m.thread_id not in threads:
            other_id = m.recipient_id if m.sender_id == user.id else m.sender_id
            other = session.get(User, other_id)
            threads[m.thread_id] = {
                "thread_id": m.thread_id,
                "subject": m.subject,
                "other": other,
                "last": m,
                "unread": 0,
            }
        if m.recipient_id == user.id and not m.read:
            threads[m.thread_id]["unread"] += 1

    lecturers = session.exec(select(User).where(User.role == Role.lecturer)).all()

    return templates.TemplateResponse(
        "portal/messages_inbox.html",
        {"request": request, "user": user,
         "threads": list(threads.values()), "lecturers": lecturers},
    )


@router.get("/thread/{thread_id}")
def view_thread(thread_id: str, request: Request,
                user: User = Depends(require_user),
                session: Session = Depends(get_session)):
    msgs = session.exec(
        select(Message).where(Message.thread_id == thread_id)
        .order_by(Message.sent_at.asc())
    ).all()
    if not msgs or not any(m.sender_id == user.id or m.recipient_id == user.id for m in msgs):
        raise HTTPException(404, "Thread not found")

    # mark as read
    for m in msgs:
        if m.recipient_id == user.id and not m.read:
            m.read = True
            session.add(m)
    session.commit()

    other_id = msgs[0].recipient_id if msgs[0].sender_id == user.id else msgs[0].sender_id
    other = session.get(User, other_id)

    return templates.TemplateResponse(
        "portal/messages_thread.html",
        {"request": request, "user": user, "messages": msgs,
         "thread_id": thread_id, "other": other, "subject": msgs[0].subject},
    )


@router.post("/new")
def new_thread(
    request: Request,
    recipient_id: int = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    recipient = session.get(User, recipient_id)
    if not recipient:
        raise HTTPException(400, "Invalid recipient")
    thread_id = str(uuid.uuid4())
    msg = Message(thread_id=thread_id, sender_id=user.id, recipient_id=recipient.id,
                  subject=subject.strip(), body=body.strip())
    session.add(msg); session.commit()
    return RedirectResponse(url=f"/app/messages/thread/{thread_id}", status_code=303)


@router.post("/thread/{thread_id}/reply")
def reply(
    thread_id: str,
    body: str = Form(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    last = session.exec(
        select(Message).where(Message.thread_id == thread_id)
        .order_by(Message.sent_at.desc())
    ).first()
    if not last or (last.sender_id != user.id and last.recipient_id != user.id):
        raise HTTPException(404, "Thread not found")
    other_id = last.recipient_id if last.sender_id == user.id else last.sender_id
    msg = Message(thread_id=thread_id, sender_id=user.id, recipient_id=other_id,
                  subject=last.subject, body=body.strip())
    session.add(msg); session.commit()
    return RedirectResponse(url=f"/app/messages/thread/{thread_id}", status_code=303)
