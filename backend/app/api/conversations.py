"""Conversation management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Conversation, Message, Seller, ConversationStatus
from app.api.auth import get_current_seller

router = APIRouter()


@router.get("")
async def list_conversations(
    status: str = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    query = select(Conversation).where(Conversation.seller_id == seller.id)
    if status:
        query = query.where(Conversation.status == ConversationStatus(status))
    query = query.order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit)

    result = await db.execute(query)
    conversations = result.scalars().all()

    total = await db.scalar(
        select(func.count(Conversation.id)).where(Conversation.seller_id == seller.id)
    )

    return {
        "conversations": [_conv_to_dict(c) for c in conversations],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conv_to_dict(conv)


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    return {
        "messages": [_msg_to_dict(m) for m in messages],
        "conversation_id": conversation_id,
    }


@router.post("/{conversation_id}/send")
async def send_message(
    conversation_id: int,
    request: dict,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    """Manually send a message (override AI)."""
    from app.services.whatsapp import WhatsAppClient
    from app.models.models import MessageCategory

    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    wa_client = WhatsAppClient(
        access_token=seller.meta_access_token or "",
        phone_number_id=seller.whatsapp_phone_id or "",
    )
    result = await wa_client.send_text_message(conv.customer_phone, text)

    msg = Message(
        conversation_id=conversation_id,
        direction="outbound",
        content=text,
        message_type="text",
        category=MessageCategory.SERVICE,
        ai_generated=False,
    )
    db.add(msg)

    return {"status": "sent", "message": _msg_to_dict(msg)}


@router.post("/{conversation_id}/escalate")
async def escalate_conversation(
    conversation_id: int,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.status = ConversationStatus.ESCALATED
    return {"status": "escalated"}


@router.post("/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: int,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.status = ConversationStatus.RESOLVED
    return {"status": "resolved"}


def _conv_to_dict(conv: Conversation) -> dict:
    return {
        "id": conv.id,
        "customer_phone": conv.customer_phone,
        "customer_name": conv.customer_name,
        "status": conv.status.value if conv.status else None,
        "language": conv.language,
        "ai_confidence_avg": conv.ai_confidence_avg,
        "is_opted_in": conv.is_opted_in,
        "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
    }


def _msg_to_dict(msg: Message) -> dict:
    return {
        "id": msg.id,
        "direction": msg.direction,
        "content": msg.content,
        "message_type": msg.message_type,
        "category": msg.category.value if msg.category else None,
        "intent": msg.intent.value if msg.intent else None,
        "ai_confidence": msg.ai_confidence,
        "ai_generated": msg.ai_generated,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    }
