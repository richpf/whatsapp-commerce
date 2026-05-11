"""Survey submission endpoint."""

from datetime import datetime
from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import text

from app.db.database import engine

router = APIRouter()

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS survey_responses (
        id SERIAL PRIMARY KEY,
        order_volume TEXT,
        order_tracking TEXT,
        monthly_spend TEXT,
        ban_worry TEXT,
        willingness_to_pay TEXT,
        missing_feature TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
"""


class SurveyRequest(BaseModel):
    order_volume: str | None = None
    order_tracking: str | None = None
    monthly_spend: str | None = None
    ban_worry: str | None = None
    willingness_to_pay: str | None = None
    missing_feature: str | None = None


class SurveyResponse(BaseModel):
    success: bool
    message: str
    total_responses: int


@router.post("/submit", response_model=SurveyResponse)
async def submit_survey(
    data: SurveyRequest,
    source: str = Query(default=None, description="Referral source (e.g. reddit, linkedin)"),
):
    """Submit a survey response."""
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))
        await conn.execute(
            text(
                "INSERT INTO survey_responses "
                "(order_volume, order_tracking, monthly_spend, ban_worry, willingness_to_pay, missing_feature, source, created_at) "
                "VALUES (:order_volume, :order_tracking, :monthly_spend, :ban_worry, :willingness_to_pay, :missing_feature, :source, :now)"
            ),
            {
                "order_volume": data.order_volume,
                "order_tracking": data.order_tracking,
                "monthly_spend": data.monthly_spend,
                "ban_worry": data.ban_worry,
                "willingness_to_pay": data.willingness_to_pay,
                "missing_feature": data.missing_feature,
                "source": source,
                "now": datetime.utcnow(),
            },
        )
        result = await conn.execute(text("SELECT COUNT(*) FROM survey_responses"))
        count = result.scalar()

    return SurveyResponse(
        success=True,
        message="Thank you for your response!",
        total_responses=count,
    )


@router.get("/count")
async def survey_count():
    """Get total survey response count (public)."""
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))
        result = await conn.execute(text("SELECT COUNT(*) FROM survey_responses"))
        count = result.scalar()
    return {"count": count}
