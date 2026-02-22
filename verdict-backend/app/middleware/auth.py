from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.config import settings


def _extract_token_from_request(request: Request) -> str | None:
    """Extract a raw JWT from httpOnly cookie or Authorization Bearer header.

    Cookie takes precedence (browser clients). Bearer header is supported as
    a fallback for curl, Postman, and mobile clients.
    """
    cookie_val = request.cookies.get("access_token", "")
    if cookie_val:
        return cookie_val.removeprefix("Bearer ").strip() or None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip() or None

    return None


async def require_auth(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = _extract_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail={"code": "TOKEN_MISSING"})

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail={"code": "TOKEN_INVALID"})
    except JWTError:
        raise HTTPException(status_code=401, detail={"code": "TOKEN_INVALID"})

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail={"code": "ACCOUNT_INACTIVE"})

    return user
