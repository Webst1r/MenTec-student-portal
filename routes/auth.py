from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, Role
from ..security import (
    hash_password, verify_password, create_session_token,
    SESSION_COOKIE, SESSION_MAX_AGE, get_current_user,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/login")
def login_form(request: Request, session: Session = Depends(get_session), next: str = "/app"):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": get_current_user(request, session), "error": None, "next": next},
    )


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/app"),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email.lower().strip())).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "user": None, "error": "Invalid email or password.", "next": next},
            status_code=400,
        )
    token = create_session_token(user.id)
    resp = RedirectResponse(url=next or "/app", status_code=303)
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_MAX_AGE,
                    httponly=True, samesite="lax")
    return resp


@router.get("/signup")
def signup_form(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse(
        "auth/signup.html",
        {"request": request, "user": get_current_user(request, session), "error": None},
    )


@router.post("/signup")
def signup_submit(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    email = email.lower().strip()
    if len(password) < 8:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "user": None, "error": "Password must be at least 8 characters."},
            status_code=400,
        )
    if session.exec(select(User).where(User.email == email)).first():
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "user": None, "error": "An account with that email already exists."},
            status_code=400,
        )
    user = User(email=email, full_name=full_name.strip(),
                password_hash=hash_password(password), role=Role.student)
    session.add(user); session.commit(); session.refresh(user)
    token = create_session_token(user.id)
    resp = RedirectResponse(url="/app", status_code=303)
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_MAX_AGE,
                    httponly=True, samesite="lax")
    return resp


@router.post("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie(SESSION_COOKIE)
    return resp
