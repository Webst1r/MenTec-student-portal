import os, secrets
from pathlib import Path
from fastapi import APIRouter, Request, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, Document
from ..security import require_user
from ..config import UPLOAD_DIR, MAX_UPLOAD_BYTES

router = APIRouter(prefix="/app/documents")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("")
def list_docs(request: Request, user: User = Depends(require_user),
              session: Session = Depends(get_session)):
    docs = session.exec(
        select(Document).where(Document.owner_id == user.id)
        .order_by(Document.uploaded_at.desc())
    ).all()
    return templates.TemplateResponse(
        "portal/documents.html",
        {"request": request, "user": user, "documents": docs},
    )


@router.post("/upload")
async def upload_doc(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    if not file.filename:
        raise HTTPException(400, "No file provided.")
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds 25 MB limit.")

    ext = Path(file.filename).suffix
    stored = f"{user.id}_{secrets.token_hex(8)}{ext}"
    target = UPLOAD_DIR / stored
    target.write_bytes(contents)

    doc = Document(
        owner_id=user.id,
        original_name=file.filename,
        stored_name=stored,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(contents),
    )
    session.add(doc); session.commit()
    return RedirectResponse(url="/app/documents", status_code=303)


@router.get("/{doc_id}/download")
def download_doc(doc_id: int, user: User = Depends(require_user),
                 session: Session = Depends(get_session)):
    doc = session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(404, "Not found")
    path = UPLOAD_DIR / doc.stored_name
    if not path.exists():
        raise HTTPException(404, "File missing on disk")
    return FileResponse(path, media_type=doc.mime_type, filename=doc.original_name)


@router.post("/{doc_id}/delete")
def delete_doc(doc_id: int, user: User = Depends(require_user),
               session: Session = Depends(get_session)):
    doc = session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(404, "Not found")
    path = UPLOAD_DIR / doc.stored_name
    if path.exists():
        try: path.unlink()
        except OSError: pass
    session.delete(doc); session.commit()
    return RedirectResponse(url="/app/documents", status_code=303)
