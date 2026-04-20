"""Seller authentication endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.models import Seller, PlanTier

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: str
    password: str
    business_name: str
    phone_number: Optional[str] = None
    language: Optional[str] = "en"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    seller: dict

class SellerUpdate(BaseModel):
    business_name: Optional[str] = None
    phone_number: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    store_type: Optional[str] = None
    store_config: Optional[dict] = None
    whatsapp_phone_id: Optional[str] = None
    whatsapp_business_id: Optional[str] = None
    meta_access_token: Optional[str] = None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def create_access_token(seller_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode = {"sub": str(seller_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_seller(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Seller:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        seller_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    seller = await db.get(Seller, seller_id)
    if not seller or not seller.is_active:
        raise HTTPException(status_code=401, detail="Seller not found or inactive")
    return seller


def seller_to_dict(seller: Seller) -> dict:
    return {
        "id": seller.id,
        "email": seller.email,
        "business_name": seller.business_name,
        "phone_number": seller.phone_number,
        "plan": seller.plan.value,
        "store_type": seller.store_type.value if seller.store_type else None,
        "is_verified": seller.is_verified,
        "setup_completed": seller.setup_completed,
        "language": seller.language,
        "timezone": seller.timezone,
        "created_at": seller.created_at.isoformat() if seller.created_at else None,
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    existing = await db.execute(select(Seller).where(Seller.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    seller = Seller(
        email=req.email,
        hashed_password=pwd_context.hash(req.password),
        business_name=req.business_name,
        phone_number=req.phone_number,
        language=req.language or "en",
        plan=PlanTier.FREE,
    )
    db.add(seller)
    await db.flush()

    token = create_access_token(seller.id)
    return TokenResponse(access_token=token, seller=seller_to_dict(seller))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.email == req.email))
    seller = result.scalar_one_or_none()

    if not seller or not pwd_context.verify(req.password, seller.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not seller.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(seller.id)
    return TokenResponse(access_token=token, seller=seller_to_dict(seller))


@router.get("/me")
async def get_me(seller: Seller = Depends(get_current_seller)):
    return seller_to_dict(seller)


@router.patch("/me")
async def update_me(
    req: SellerUpdate,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(seller, key):
            setattr(seller, key, value)
    seller.updated_at = datetime.utcnow()
    return seller_to_dict(seller)


@router.post("/setup-complete")
async def mark_setup_complete(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    seller.setup_completed = True
    seller.is_verified = True
    return {"status": "ok", "setup_completed": True}
