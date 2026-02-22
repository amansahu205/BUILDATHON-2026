import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from nanoid import generate
from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_ACCESS_TTL_HOURS = 8
_REFRESH_TTL_DAYS = 30


def _access_token(user: User) -> str:
    return jwt.encode(
        {
            "sub": user.id,
            "firmId": user.firm_id,
            "role": user.role,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=_ACCESS_TTL_HOURS),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )


def _make_refresh_token(user: User) -> str:
    return jwt.encode(
        {
            "sub": user.id,
            "firmId": user.firm_id,
            "jti": generate(),
            "exp": datetime.utcnow() + timedelta(days=_REFRESH_TTL_DAYS),
        },
        settings.JWT_REFRESH_SECRET,
        algorithm="HS256",
    )


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Write httpOnly auth cookies — matches BACKEND_STRUCTURE.md §3 spec."""
    is_prod = getattr(settings, "ENVIRONMENT", "development") == "production"
    response.set_cookie(
        "access_token",
        f"Bearer {access_token}",
        httponly=True,
        samesite="strict",
        secure=is_prod,
        max_age=_ACCESS_TTL_HOURS * 3600,
    )
    response.set_cookie(
        "refresh_token",
        f"Bearer {refresh_token}",
        httponly=True,
        samesite="strict",
        secure=is_prod,
        max_age=_REFRESH_TTL_DAYS * 24 * 3600,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", samesite="strict")
    response.delete_cookie("refresh_token", samesite="strict")


@router.post("/login")
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS"})

    if not pwd_context.verify(body.password, user.password_hash):
        user.login_attempts = (user.login_attempts or 0) + 1
        await db.commit()
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS"})

    if not user.is_active:
        raise HTTPException(403, detail={"code": "ACCOUNT_INACTIVE"})

    access_token = _access_token(user)
    refresh_token = _make_refresh_token(user)

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=_REFRESH_TTL_DAYS),
    ))
    user.last_login_at = datetime.utcnow()
    user.login_attempts = 0
    await db.commit()

    _set_auth_cookies(response, access_token, refresh_token)

    return {
        "success": True,
        "data": {
            "user": {
                "id": user.id,
                "firmId": user.firm_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
            }
        },
    }


@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Issue a new access token using the refresh_token cookie."""
    cookie_val = request.cookies.get("refresh_token", "")
    raw_token = cookie_val.removeprefix("Bearer ").strip()
    if not raw_token:
        raise HTTPException(401, detail={"code": "TOKEN_MISSING"})

    try:
        payload = jwt.decode(raw_token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
    except JWTError:
        raise HTTPException(401, detail={"code": "TOKEN_EXPIRED"})

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    rt = result.scalar_one_or_none()
    if not rt:
        raise HTTPException(401, detail={"code": "TOKEN_REVOKED"})

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(403, detail={"code": "ACCOUNT_INACTIVE"})

    new_access = _access_token(user)
    is_prod = getattr(settings, "ENVIRONMENT", "development") == "production"
    response.set_cookie(
        "access_token",
        f"Bearer {new_access}",
        httponly=True,
        samesite="strict",
        secure=is_prod,
        max_age=_ACCESS_TTL_HOURS * 3600,
    )

    expires_at = (datetime.utcnow() + timedelta(hours=_ACCESS_TTL_HOURS)).isoformat() + "Z"
    return {"success": True, "data": {"expiresAt": expires_at}}


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Revoke refresh token and clear auth cookies."""
    cookie_val = request.cookies.get("refresh_token", "")
    raw_token = cookie_val.removeprefix("Bearer ").strip()

    if raw_token:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        rt = result.scalar_one_or_none()
        if rt:
            rt.revoked_at = datetime.utcnow()
            await db.commit()

    _clear_auth_cookies(response)
    return {"success": True, "message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Revoke ALL refresh tokens for the current user (all devices)."""
    from app.middleware.auth import _extract_token_from_request
    token = _extract_token_from_request(request)
    if not token:
        raise HTTPException(401, detail={"code": "TOKEN_MISSING"})

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, detail={"code": "TOKEN_INVALID"})

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    tokens = result.scalars().all()
    now = datetime.utcnow()
    for rt in tokens:
        rt.revoked_at = now
    await db.commit()

    _clear_auth_cookies(response)
    return {"success": True, "message": "All sessions revoked", "sessionsRevoked": len(tokens)}
