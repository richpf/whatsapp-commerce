"""Waitlist signup endpoint."""

from datetime import datetime
from fastapi import APIRouter, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text

from app.db.database import engine
from app.models.models import WaitlistEntry

router = APIRouter()


class WaitlistRequest(BaseModel):
    email: EmailStr
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

    async with engine.begin() as conn:
        # Check if already on waitlist
        result = await conn.execute(
            text("SELECT id FROM waitlist WHERE email = :email"),
            {"email": data.email.lower()},
        )
        existing = result.fetchone()
        if existing:
            # Get position
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
                "INSERT INTO waitlist (email, source, ip_address, user_agent, created_at) "
                "VALUES (:email, :source, :ip, :ua, :now)"
            ),
            {
                "email": data.email.lower(),
                "source": data.source,
                "ip": ip,
                "ua": ua[:500] if ua else None,
                "now": datetime.utcnow(),
            },
        )

        # Get position
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
        result = await conn.execute(text("SELECT COUNT(*) FROM waitlist"))
        count = result.scalar()
    return {"count": count}
