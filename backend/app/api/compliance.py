"""Compliance dashboard endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Seller, ComplianceLog, Template, TemplateStatus, MessageCategory
from app.api.auth import get_current_seller
from app.services.compliance import compliance_engine

router = APIRouter()


@router.get("/overview")
async def compliance_overview(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive compliance overview."""
    ban_risk = await compliance_engine.get_ban_risk_assessment(db, seller.id)
    costs = await compliance_engine.get_monthly_costs(db, seller.id)
    plan_usage = await compliance_engine.check_plan_limit(db, seller.id)

    return {
        "ban_risk": ban_risk,
        "costs": costs,
        "plan_usage": plan_usage,
    }


@router.get("/spam-score")
async def get_spam_score(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await compliance_engine.calculate_spam_score(db, seller.id)


@router.get("/rate-limits")
async def get_rate_limit_status(
    phone: str = "",
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await compliance_engine.check_rate_limit(db, seller.id, phone)


@router.get("/costs")
async def get_costs(
    month: str = None,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await compliance_engine.get_monthly_costs(db, seller.id, month)


@router.get("/logs")
async def get_compliance_logs(
    severity: str = None,
    limit: int = Query(default=50, le=200),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    query = select(ComplianceLog).where(ComplianceLog.seller_id == seller.id)
    if severity:
        query = query.where(ComplianceLog.severity == severity)
    query = query.order_by(desc(ComplianceLog.created_at)).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "severity": log.severity,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    }


@router.get("/templates")
async def list_templates(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Template).where(Template.seller_id == seller.id).order_by(Template.name)
    )
    templates = result.scalars().all()
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "language": t.language,
                "category": t.category.value if t.category else None,
                "content": t.content,
                "status": t.status.value if t.status else None,
                "is_festival": t.is_festival,
                "festival_name": t.festival_name,
                "uses_count": t.uses_count,
            }
            for t in templates
        ]
    }


@router.post("/templates")
async def create_template(
    request: dict,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    template = Template(
        seller_id=seller.id,
        name=request["name"],
        language=request.get("language", "en"),
        category=MessageCategory(request.get("category", "utility")),
        content=request["content"],
        variables=request.get("variables"),
        is_festival=request.get("is_festival", False),
        festival_name=request.get("festival_name"),
        status=TemplateStatus.PENDING,
    )
    db.add(template)
    await db.flush()
    return {"id": template.id, "status": "pending", "message": "Template submitted for approval"}
