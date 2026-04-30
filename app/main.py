from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .db import init_db
from .seed import seed
from .security import get_current_user, get_session
from .routers import (
    public, auth, portal, documents, messages,
    courses, announcements, calendar as cal, profile, admin,
)

BASE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE / "templates"))

app = FastAPI(title="Mentec Student Portal")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

# Make current_user available in all templates
@app.middleware("http")
async def attach_user(request: Request, call_next):
    response = await call_next(request)
    return response


@app.on_event("startup")
def on_start() -> None:
    init_db()
    seed()


# Routers
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(portal.router)
app.include_router(documents.router)
app.include_router(messages.router)
app.include_router(courses.router)
app.include_router(announcements.router)
app.include_router(cal.router)
app.include_router(profile.router)
app.include_router(admin.router)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    from sqlmodel import Session
    from .db import engine
    with Session(engine) as s:
        user = get_current_user(request, s)
    return templates.TemplateResponse(
        "404.html", {"request": request, "user": user}, status_code=404
    )
