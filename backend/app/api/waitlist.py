"""Waitlist signup endpoint."""

from datetime import datetime
from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import text

from app.db.database import engine

router = APIRouter()


class WaitlistRequest(BaseModel):
    email: str
    whatsapp_number: str | None = None
    whatsapp_opt_in: bool = False
    source: str = "landing_page"


class WaitlistResponse(BaseModel):
    success: bool
    message: str
    position: int | None = None


@router.post("/join", response_model=WaitlistResponse)
async def join_waitlist(data: WaitlistRequest, request: Request):
    """Add an email to the waitlist."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")

    # Normalize WhatsApp number — strip spaces, ensure + prefix
    wa_number = None
    if data.whatsapp_number:
        cleaned = data.whatsapp_number.strip().replace(" ", "").replace("-", "")
        if cleaned and len(cleaned) >= 7:
            if not cleaned.startswith("+"):
                cleaned = "+" + cleaned
            wa_number = cleaned

    async with engine.begin() as conn:
        # Ensure table exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS waitlist (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                whatsapp_number VARCHAR(20),
                whatsapp_opt_in BOOLEAN DEFAULT FALSE,
                source VARCHAR(100) DEFAULT 'landing_page',
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        # Check if already on waitlist
        result = await conn.execute(
            text("SELECT id FROM waitlist WHERE email = :email"),
            {"email": data.email.lower()},
        )
        existing = result.fetchone()
        if existing:
            # Update WhatsApp number if provided and not previously set
            if wa_number:
                await conn.execute(
                    text("UPDATE waitlist SET whatsapp_number = :wa, whatsapp_opt_in = :opt WHERE id = :id AND (whatsapp_number IS NULL OR whatsapp_number = '')"),
                    {"wa": wa_number, "opt": data.whatsapp_opt_in, "id": existing[0]},
                )
            pos_result = await conn.execute(
                text("SELECT COUNT(*) FROM waitlist WHERE id <= :id"),
                {"id": existing[0]},
            )
            position = pos_result.scalar()
            return WaitlistResponse(
                success=True,
                message="You're already on the waitlist!",
                position=position,
            )

        # Insert
        await conn.execute(
            text(
                "INSERT INTO waitlist (email, whatsapp_number, whatsapp_opt_in, source, ip_address, user_agent, created_at) "
                "VALUES (:email, :wa, :opt, :source, :ip, :ua, :now)"
            ),
            {
                "email": data.email.lower(),
                "wa": wa_number,
                "opt": data.whatsapp_opt_in and wa_number is not None,
                "source": data.source,
                "ip": ip,
                "ua": ua[:500] if ua else None,
                "now": datetime.utcnow(),
            },
        )

        pos_result = await conn.execute(text("SELECT COUNT(*) FROM waitlist"))
        position = pos_result.scalar()

    return WaitlistResponse(
        success=True,
        message="You're on the list!",
        position=position,
    )


@router.get("/count")
async def waitlist_count():
    """Get total waitlist count (public)."""
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS waitlist (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                whatsapp_number VARCHAR(20),
                whatsapp_opt_in BOOLEAN DEFAULT FALSE,
                source VARCHAR(100) DEFAULT 'landing_page',
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        result = await conn.execute(text("SELECT COUNT(*) FROM waitlist"))
        count = result.scalar()
    return {"count": count}
