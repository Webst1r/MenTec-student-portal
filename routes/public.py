from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session

from ..security import get_current_user
from ..db import get_session

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _ctx(request: Request, session: Session, **extra):
    return {"request": request, "user": get_current_user(request, session), **extra}


@router.get("/")
def home(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("public/home.html", _ctx(request, session))


@router.get("/solutions")
def solutions(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("public/solutions.html", _ctx(request, session))


@router.get("/track-record")
def track_record(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("public/track_record.html", _ctx(request, session))


@router.get("/about")
def about(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("public/about.html", _ctx(request, session))


@router.get("/contact")
def contact(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("public/contact.html", _ctx(request, session))
