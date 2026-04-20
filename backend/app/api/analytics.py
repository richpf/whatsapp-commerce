"""Analytics endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import (
    Seller, Conversation, Message, Order, ConversationStatus, MessageCategory
)
from app.api.auth import get_current_seller
from app.services.cart_recovery import cart_recovery_service

router = APIRouter()


@router.get("/overview")
async def analytics_overview(
    days: int = Query(default=30, le=90),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)

    # Messages
    total_messages = await db.scalar(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.seller_id == seller.id, Message.created_at >= since)
    ) or 0

    inbound = await db.scalar(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.seller_id == seller.id, Message.direction == "inbound",
               Message.created_at >= since)
    ) or 0

    outbound = total_messages - inbound

    ai_messages = await db.scalar(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.seller_id == seller.id, Message.ai_generated == True,
               Message.created_at >= since)
    ) or 0

    # Conversations
    total_conversations = await db.scalar(
        select(func.count(Conversation.id))
        .where(Conversation.seller_id == seller.id, Conversation.created_at >= since)
    ) or 0

    escalated = await db.scalar(
        select(func.count(Conversation.id))
        .where(Conversation.seller_id == seller.id,
               Conversation.status == ConversationStatus.ESCALATED,
               Conversation.created_at >= since)
    ) or 0

    resolved = await db.scalar(
        select(func.count(Conversation.id))
        .where(Conversation.seller_id == seller.id,
               Conversation.status == ConversationStatus.RESOLVED,
               Conversation.created_at >= since)
    ) or 0

    # Average AI confidence
    avg_confidence = await db.scalar(
        select(func.avg(Message.ai_confidence))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.seller_id == seller.id, Message.ai_confidence.isnot(None),
               Message.created_at >= since)
    )

    # Orders & Revenue
    total_orders = await db.scalar(
        select(func.count(Order.id))
        .where(Order.seller_id == seller.id, Order.created_at >= since)
    ) or 0

    revenue = await db.scalar(
        select(func.sum(Order.total_amount))
        .where(Order.seller_id == seller.id, Order.payment_status == "paid",
               Order.created_at >= since)
    ) or 0.0

    # Cart recovery
    recovery = await cart_recovery_service.get_recovery_stats(db, seller.id)

    return {
        "period_days": days,
        "messages": {
            "total": total_messages,
            "inbound": inbound,
            "outbound": outbound,
            "ai_generated": ai_messages,
            "ai_rate": round(ai_messages / max(outbound, 1) * 100, 1),
        },
        "conversations": {
            "total": total_conversations,
            "escalated": escalated,
            "resolved": resolved,
            "escalation_rate": round(escalated / max(total_conversations, 1) * 100, 1),
        },
        "ai_confidence_avg": round(float(avg_confidence or 0), 2),
        "orders": {
            "total": total_orders,
            "revenue": round(float(revenue), 2),
        },
        "cart_recovery": recovery,
    }


@router.get("/messages/daily")
async def daily_message_stats(
    days: int = Query(default=30, le=90),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Message.created_at).label("date"),
            Message.direction,
            func.count(Message.id),
        )
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.seller_id == seller.id, Message.created_at >= since)
        .group_by(func.date(Message.created_at), Message.direction)
        .order_by(func.date(Message.created_at))
    )

    daily = {}
    for row in result:
        date_str = str(row[0])
        if date_str not in daily:
            daily[date_str] = {"date": date_str, "inbound": 0, "outbound": 0}
        daily[date_str][row[1]] = row[2]

    return {"daily": list(daily.values())}
