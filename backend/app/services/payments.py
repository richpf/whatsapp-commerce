"""Payment link generation: Razorpay, Stripe, generic checkout links."""

import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Generate payment links for in-chat payments."""

    def __init__(self):
        self.stripe = None
        self.razorpay = None
        self._init_providers()

    def _init_providers(self):
        if settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                self.stripe = stripe
                logger.info("Stripe initialized")
            except Exception as e:
                logger.warning(f"Stripe init failed: {e}")

        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            try:
                import razorpay
                self.razorpay = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                logger.info("Razorpay initialized")
            except Exception as e:
                logger.warning(f"Razorpay init failed: {e}")

    async def create_stripe_payment_link(
        self, amount: float, currency: str = "inr",
        product_name: str = "Order", customer_email: str = None,
        metadata: dict = None
    ) -> dict:
        """Create a Stripe payment link."""
        if not self.stripe:
            return self._mock_payment_link("stripe", amount, currency, product_name)

        try:
            # Create a price
            price = self.stripe.Price.create(
                unit_amount=int(amount * 100),  # Stripe uses cents
                currency=currency.lower(),
                product_data={"name": product_name},
            )
            # Create payment link
            link = self.stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}],
                metadata=metadata or {},
            )
            return {
                "provider": "stripe",
                "url": link.url,
                "id": link.id,
                "amount": amount,
                "currency": currency,
            }
        except Exception as e:
            logger.error(f"Stripe payment link error: {e}")
            return {"provider": "stripe", "error": str(e)}

    async def create_razorpay_payment_link(
        self, amount: float, currency: str = "INR",
        product_name: str = "Order", customer_name: str = None,
        customer_phone: str = None, metadata: dict = None
    ) -> dict:
        """Create a Razorpay payment link."""
        if not self.razorpay:
            return self._mock_payment_link("razorpay", amount, currency, product_name)

        try:
            data = {
                "amount": int(amount * 100),  # Razorpay uses paise
                "currency": currency.upper(),
                "description": product_name,
                "customer": {},
                "notify": {"sms": True, "email": False},
                "callback_url": f"{settings.API_BASE_URL}/api/payments/callback",
                "callback_method": "get",
            }
            if customer_name:
                data["customer"]["name"] = customer_name
            if customer_phone:
                data["customer"]["contact"] = customer_phone
            if metadata:
                data["notes"] = metadata

            link = self.razorpay.payment_link.create(data)
            return {
                "provider": "razorpay",
                "url": link.get("short_url", link.get("url", "")),
                "id": link.get("id"),
                "amount": amount,
                "currency": currency,
            }
        except Exception as e:
            logger.error(f"Razorpay payment link error: {e}")
            return {"provider": "razorpay", "error": str(e)}

    async def create_checkout_link(
        self, amount: float, currency: str = "INR",
        product_name: str = "Order", order_id: str = None,
        provider: str = "auto", customer_phone: str = None,
        customer_name: str = None
    ) -> dict:
        """Create a payment link using the best available provider."""
        metadata = {"order_id": order_id} if order_id else {}

        if provider == "razorpay" or (provider == "auto" and self.razorpay):
            return await self.create_razorpay_payment_link(
                amount, currency, product_name, customer_name, customer_phone, metadata
            )
        elif provider == "stripe" or (provider == "auto" and self.stripe):
            return await self.create_stripe_payment_link(
                amount, currency, product_name, metadata=metadata
            )
        else:
            return self._mock_payment_link("generic", amount, currency, product_name)

    def _mock_payment_link(self, provider: str, amount: float, currency: str,
                           product_name: str) -> dict:
        """Generate a mock payment link for demo/test mode."""
        import hashlib
        import time
        link_id = hashlib.md5(f"{amount}{time.time()}".encode()).hexdigest()[:12]
        return {
            "provider": provider,
            "url": f"{settings.API_BASE_URL}/pay/{link_id}",
            "id": link_id,
            "amount": amount,
            "currency": currency,
            "test_mode": True,
        }


# Singleton
payment_service = PaymentService()
