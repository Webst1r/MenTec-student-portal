from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import bcrypt
from sqlmodel import Session, select

from .config import SECRET_KEY, SESSION_COOKIE, SESSION_MAX_AGE
from .db import get_session
from .models import User, Role

serializer = URLSafeTimedSerializer(SECRET_KEY, salt="mentec-session")


def _truncate(pw: str) -> bytes:
    # bcrypt limits to 72 bytes
    return pw.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_truncate(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def create_session_token(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})


def read_session_token(token: str) -> Optional[int]:
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        return int(data.get("uid"))
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None


def get_current_user(
    request: Request, session: Session = Depends(get_session)
) -> Optional[User]:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    uid = read_session_token(token)
    if uid is None:
        return None
    return session.get(User, uid)


def require_user(
    request: Request, session: Session = Depends(get_session)
) -> User:
    user = get_current_user(request, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"/login?next={request.url.path}"},
        )
    return user


def require_role(*roles: Role):
    def _checker(user: User = Depends(require_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _checker
