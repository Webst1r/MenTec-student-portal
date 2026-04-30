from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from ..db import get_session
from ..models import User
from ..security import require_user

router = APIRouter(prefix="/app/profile")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
def profile_page(request: Request, user: User = Depends(require_user)):
    return templates.TemplateResponse(
        "portal/profile.html", {"request": request, "user": user, "saved": False}
    )


@router.post("")
def update_profile(
    full_name: str = Form(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    user.full_name = full_name.strip()
    session.add(user); session.commit()
    return RedirectResponse(url="/app/profile", status_code=303)
