import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _access_token(user: User) -> str:
    return jwt.encode(
        {
            "sub": user.id,
            "firmId": user.firm_id,
            "role": user.role,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=8),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )


def _refresh_token(user: User) -> str:
    from nanoid import generate
    return jwt.encode(
        {
            "sub": user.id,
            "firmId": user.firm_id,
            "jti": generate(),
            "exp": datetime.utcnow() + timedelta(days=30),
        },
        settings.JWT_REFRESH_SECRET,
        algorithm="HS256",
    )


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
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
    refresh_token = _refresh_token(user)

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=30),
    ))
    user.last_login_at = datetime.utcnow()
    user.login_attempts = 0
    await db.commit()

    return {
        "success": True,
        "data": {
            "user": {
                "id": user.id,
                "firmId": user.firm_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
            },
            "accessToken": access_token,
            "refreshToken": refresh_token,
        },
    }


@router.post("/logout")
async def logout(db: AsyncSession = Depends(get_db)):
    return {"success": True, "message": "Logged out"}
