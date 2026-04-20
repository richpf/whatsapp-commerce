"""Abandoned cart detection and recovery messaging."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Order, Seller, Conversation
from app.services.whatsapp import whatsapp_client
from app.services.payments import payment_service
from app.services.compliance import compliance_engine

logger = logging.getLogger(__name__)

# Cart is considered abandoned after this many hours
ABANDONMENT_THRESHOLD_HOURS = 1
# Max recovery messages per cart
MAX_RECOVERY_ATTEMPTS = 2
# Delay between recovery attempts (hours)
RECOVERY_DELAY_HOURS = 24


class CartRecoveryService:
    """Detect abandoned carts and send recovery messages."""

    async def detect_abandoned_carts(self, db: AsyncSession, seller_id: int) -> list:
        """Find orders that are abandoned (unpaid, older than threshold)."""
        threshold = datetime.utcnow() - timedelta(hours=ABANDONMENT_THRESHOLD_HOURS)

        result = await db.execute(
            select(Order).where(
                Order.seller_id == seller_id,
                Order.payment_status == "unpaid",
                Order.status == "pending",
                Order.cart_abandoned == False,
                Order.created_at <= threshold,
            )
        )
        abandoned = result.scalars().all()

        # Mark as abandoned
        for order in abandoned:
            order.cart_abandoned = True

        return [self._order_to_dict(o) for o in abandoned]

    async def send_recovery_message(
        self, db: AsyncSession, seller_id: int, order_id: int
    ) -> dict:
        """Send a cart recovery message for an abandoned order."""
        order = await db.get(Order, order_id)
        if not order or order.seller_id != seller_id:
            return {"success": False, "error": "Order not found"}

        if not order.cart_abandoned:
            return {"success": False, "error": "Order is not abandoned"}

        if order.cart_recovered:
            return {"success": False, "error": "Already recovered"}

        # Check compliance
        seller = await db.get(Seller, seller_id)
        rate_check = await compliance_engine.check_rate_limit(db, seller_id, order.customer_phone)
        if not rate_check["allowed"]:
            return {"success": False, "error": "Rate limited", "violations": rate_check["violations"]}

        plan_check = await compliance_engine.check_plan_limit(db, seller_id)
        if not plan_check["allowed"]:
            return {"success": False, "error": "Plan limit reached"}

        # Generate payment link
        items_desc = "your items"
        if order.items:
            names = [i.get("name", "item") for i in order.items[:3]]
            items_desc = ", ".join(names)

        payment = await payment_service.create_checkout_link(
            amount=order.total_amount,
            currency=order.currency,
            product_name=items_desc,
            order_id=str(order.id),
            customer_phone=order.customer_phone,
        )

        # Send recovery message
        business_name = seller.business_name if seller else "our store"
        message = (
            f"Hi{' ' + order.customer_name if order.customer_name else ''}! 👋\n\n"
            f"You left some great items in your cart at *{business_name}*:\n"
            f"🛒 {items_desc}\n"
            f"💰 Total: {order.currency} {order.total_amount:.2f}\n\n"
            f"Complete your purchase here: {payment.get('url', 'N/A')}\n\n"
            f"This link expires in 24 hours. Need help? Just reply!"
        )

        wa_client = WhatsAppClient(
            access_token=seller.meta_access_token or "",
            phone_number_id=seller.whatsapp_phone_id or "",
        ) if seller else whatsapp_client

        result = await wa_client.send_text_message(order.customer_phone, message)

        order.recovery_sent_at = datetime.utcnow()

        return {
            "success": True,
            "message_sent": True,
            "payment_link": payment.get("url"),
            "order_id": order.id,
        }

    async def get_recovery_stats(self, db: AsyncSession, seller_id: int) -> dict:
        """Get cart recovery statistics."""
        from sqlalchemy import func

        total_abandoned = await db.scalar(
            select(func.count(Order.id)).where(
                Order.seller_id == seller_id, Order.cart_abandoned == True
            )
        ) or 0

        total_recovered = await db.scalar(
            select(func.count(Order.id)).where(
                Order.seller_id == seller_id, Order.cart_recovered == True
            )
        ) or 0

        recovery_sent = await db.scalar(
            select(func.count(Order.id)).where(
                Order.seller_id == seller_id,
                Order.cart_abandoned == True,
                Order.recovery_sent_at.isnot(None),
            )
        ) or 0

        revenue_recovered = await db.scalar(
            select(func.sum(Order.total_amount)).where(
                Order.seller_id == seller_id, Order.cart_recovered == True
            )
        ) or 0.0

        return {
            "total_abandoned": total_abandoned,
            "recovery_messages_sent": recovery_sent,
            "total_recovered": total_recovered,
            "recovery_rate": round(total_recovered / max(total_abandoned, 1) * 100, 1),
            "revenue_recovered": round(revenue_recovered, 2),
        }

    def _order_to_dict(self, order: Order) -> dict:
        return {
            "id": order.id,
            "customer_phone": order.customer_phone,
            "customer_name": order.customer_name,
            "items": order.items,
            "total_amount": order.total_amount,
            "currency": order.currency,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }


# Import here to avoid circular
from app.services.whatsapp import WhatsAppClient

cart_recovery_service = CartRecoveryService()
