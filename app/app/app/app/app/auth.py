from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException, Request

from passlib.context import CryptContext

from app.config import settings
from app.database import get_db
from app.models import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str
) -> bool:
    return pwd_context.verify(
        password,
        password_hash
    )


def create_access_token(user_id: int) -> str:

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expiration
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str) -> int:

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return int(payload["sub"])

    except (
        jwt.PyJWTError,
        KeyError,
        ValueError
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def get_current_user(
    request: Request
) -> User:

    token = request.cookies.get(
        "access_token"
    )

    if not token:

        authorization = request.headers.get(
            "Authorization",
            ""
        )

        if authorization.lower().startswith(
            "bearer "
        ):
            token = authorization[7:]

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    user_id = decode_token(token)

    with get_db() as db:

        row = db.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    if not row:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"]
    )
