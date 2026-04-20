"""Meta WhatsApp Cloud API webhook handler."""

import logging
from datetime import datetime
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import (
    Seller, Conversation, Message, ConversationStatus, MessageCategory, IntentType
)
from app.services.whatsapp import whatsapp_client, WhatsAppClient
from app.services.ai_agent import ai_agent
from app.services.compliance import compliance_engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def verify_webhook(request: Request):
    """Meta webhook verification (GET request)."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    result = whatsapp_client.verify_webhook(mode, token, challenge)
    if result:
        return Response(content=result, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle incoming WhatsApp messages."""
    payload = await request.json()
    messages = whatsapp_client.parse_webhook_payload(payload)

    for msg in messages:
        try:
            await _process_message(db, msg)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    return {"status": "ok"}


async def _process_message(db: AsyncSession, msg: dict):
    """Process a single incoming message."""
    phone_number_id = msg["phone_number_id"]
    from_number = msg["from"]
    text = msg["text"]
    contact_name = msg.get("contact_name", "")

    # Find the seller by phone_number_id
    result = await db.execute(
        select(Seller).where(Seller.whatsapp_phone_id == phone_number_id)
    )
    seller = result.scalar_one_or_none()

    if not seller:
        # Try to find any active seller (dev/single-tenant mode)
        result = await db.execute(select(Seller).where(Seller.is_active == True).limit(1))
        seller = result.scalar_one_or_none()
        if not seller:
            logger.warning(f"No seller found for phone_number_id={phone_number_id}")
            return

    # Get or create conversation
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.seller_id == seller.id,
            Conversation.customer_phone == from_number,
        )
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            seller_id=seller.id,
            customer_phone=from_number,
            customer_name=contact_name,
            status=ConversationStatus.ACTIVE,
            is_opted_in=True,
            opted_in_at=datetime.utcnow(),
        )
        db.add(conversation)
        await db.flush()

    conversation.last_message_at = datetime.utcnow()
    if contact_name and not conversation.customer_name:
        conversation.customer_name = contact_name

    # Save inbound message
    inbound = Message(
        conversation_id=conversation.id,
        direction="inbound",
        content=text,
        message_type=msg.get("type", "text"),
        category=MessageCategory.SERVICE,
        meta_message_id=msg.get("message_id"),
    )
    db.add(inbound)
    await db.flush()

    # Classify intent
    # Build conversation history
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    history = [
        {"role": "assistant" if m.direction == "outbound" else "user", "content": m.content}
        for m in reversed(history_result.scalars().all())
    ]

    classification = await ai_agent.classify_intent(text, history)
    intent = classification["intent"]
    confidence = classification["confidence"]
    language = classification.get("language", "en")

    inbound.intent = IntentType(intent) if intent in [e.value for e in IntentType] else IntentType.UNKNOWN
    inbound.ai_confidence = confidence

    # Check if human escalation needed
    if intent == "human_escalation" or confidence < 0.3:
        conversation.status = ConversationStatus.ESCALATED

    # Check compliance before responding
    rate_check = await compliance_engine.check_rate_limit(db, seller.id, from_number)
    plan_check = await compliance_engine.check_plan_limit(db, seller.id)

    if not rate_check["allowed"] or not plan_check["allowed"]:
        logger.warning(f"Compliance block for seller {seller.id}: rate={rate_check}, plan={plan_check}")
        return

    # Generate AI response
    context = {"business_name": seller.business_name}
    response = await ai_agent.generate_response(intent, text, language, context, history)

    # Send response
    wa_client = WhatsAppClient(
        access_token=seller.meta_access_token or "",
        phone_number_id=seller.whatsapp_phone_id or "",
    )
    send_result = await wa_client.send_text_message(from_number, response["text"])

    # Save outbound message
    outbound = Message(
        conversation_id=conversation.id,
        direction="outbound",
        content=response["text"],
        message_type="text",
        category=MessageCategory.SERVICE,
        intent=inbound.intent,
        ai_confidence=confidence,
        ai_generated=response.get("ai_generated", False),
        meta_message_id=send_result.get("messages", [{}])[0].get("id") if isinstance(send_result, dict) else None,
    )
    db.add(outbound)
    await db.flush()

    # Log cost
    await compliance_engine.log_message_cost(db, seller.id, outbound.id, "service")

    # Update conversation AI confidence average
    conversation.ai_confidence_avg = confidence
    conversation.language = language


@router.post("/test")
async def test_message(request: Request, db: AsyncSession = Depends(get_db)):
    """Test endpoint to simulate an incoming WhatsApp message."""
    data = await request.json()
    phone = data.get("from", "+919876543210")
    text = data.get("text", "Hello")
    seller_id = data.get("seller_id", 1)

    mock_msg = {
        "phone_number_id": "test",
        "from": phone,
        "message_id": "test_msg_id",
        "timestamp": str(int(datetime.utcnow().timestamp())),
        "type": "text",
        "text": text,
        "contact_name": data.get("name", "Test User"),
    }

    await _process_message(db, mock_msg)
    return {"status": "processed", "from": phone, "text": text}
