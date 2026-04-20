"""Billing and subscription management endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.models import Seller, PlanTier
from app.api.auth import get_current_seller

logger = logging.getLogger(__name__)
router = APIRouter()

PLAN_PRICES = {
    PlanTier.FREE: {"monthly": 0, "annual": 0, "stripe_price_monthly": None, "stripe_price_annual": None},
    PlanTier.STARTER: {"monthly": 19, "annual": 182, "stripe_price_monthly": "price_starter_monthly",
                       "stripe_price_annual": "price_starter_annual"},
    PlanTier.PRO: {"monthly": 39, "annual": 374, "stripe_price_monthly": "price_pro_monthly",
                   "stripe_price_annual": "price_pro_annual"},
    PlanTier.SCALE: {"monthly": 79, "annual": 758, "stripe_price_monthly": "price_scale_monthly",
                     "stripe_price_annual": "price_scale_annual"},
}


@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {
                "id": "free", "name": "Free", "price_monthly": 0, "price_annual": 0,
                "messages": 50, "features": [
                    "50 business-initiated messages/mo", "1 WhatsApp number",
                    "Basic AI auto-replies", "Compliance dashboard",
                ],
            },
            {
                "id": "starter", "name": "Starter", "price_monthly": 19, "price_annual": 182,
                "messages": 500, "features": [
                    "500 messages/mo", "Compliance Shield",
                    "AI agent", "Order lookup", "Consumption dashboard",
                ],
            },
            {
                "id": "pro", "name": "Pro", "price_monthly": 39, "price_annual": 374,
                "messages": 2000, "features": [
                    "2,000 messages/mo", "Abandoned cart recovery",
                    "Shopify/WooCommerce/Sheets sync", "In-chat payment links",
                    "Festival campaign templates", "Priority support",
                ],
            },
            {
                "id": "scale", "name": "Scale", "price_monthly": 79, "price_annual": 758,
                "messages": 10000, "features": [
                    "10,000 messages/mo", "Team inbox (3 agents)",
                    "Broadcast campaigns", "Full analytics",
                    "All Pro features",
                ],
            },
        ]
    }


@router.get("/current")
async def get_current_plan(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    plan_info = PLAN_PRICES.get(seller.plan, PLAN_PRICES[PlanTier.FREE])
    return {
        "plan": seller.plan.value,
        "price_monthly": plan_info["monthly"],
        "stripe_customer_id": seller.stripe_customer_id,
        "stripe_subscription_id": seller.stripe_subscription_id,
    }


@router.post("/checkout")
async def create_checkout_session(
    request: dict,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for plan upgrade."""
    plan = request.get("plan", "starter")
    billing_period = request.get("period", "monthly")

    target_plan = PlanTier(plan)
    plan_info = PLAN_PRICES.get(target_plan)
    if not plan_info:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not settings.STRIPE_SECRET_KEY:
        # Mock checkout for demo
        return {
            "checkout_url": f"{settings.FRONTEND_URL}/billing/success?plan={plan}",
            "test_mode": True,
        }

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create or get customer
        if not seller.stripe_customer_id:
            customer = stripe.Customer.create(email=seller.email, name=seller.business_name)
            seller.stripe_customer_id = customer.id

        price_key = f"stripe_price_{billing_period}"
        price_id = plan_info.get(price_key)

        session = stripe.checkout.Session.create(
            customer=seller.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing?cancelled=true",
            metadata={"seller_id": str(seller.id), "plan": plan},
        )
        return {"checkout_url": session.url}
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Payment processing error")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_SECRET_KEY:
        return {"status": "ok", "test_mode": True}

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            seller_id = int(session["metadata"]["seller_id"])
            plan = session["metadata"]["plan"]
            seller = await db.get(Seller, seller_id)
            if seller:
                seller.plan = PlanTier(plan)
                seller.stripe_subscription_id = session.get("subscription")

        elif event["type"] == "customer.subscription.deleted":
            sub = event["data"]["object"]
            from sqlalchemy import select
            result = await db.execute(
                select(Seller).where(Seller.stripe_subscription_id == sub["id"])
            )
            seller = result.scalar_one_or_none()
            if seller:
                seller.plan = PlanTier.FREE
                seller.stripe_subscription_id = None

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
