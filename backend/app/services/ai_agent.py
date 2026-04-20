"""AI Agent using GPT-4o-mini for intent classification and response generation."""

import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """You are a commerce assistant AI for a WhatsApp-based e-commerce platform.
Classify the customer's message into exactly ONE intent:
- order_status: asking about order tracking, delivery, shipment
- product_inquiry: asking about products, prices, availability, features
- returns: requesting returns, refunds, exchanges
- cart_recovery: responding to cart abandonment message, showing purchase interest
- size_guidance: asking about sizing, fit, measurements
- payment: asking about payment methods, payment issues, payment links
- greeting: hello, hi, hey, or similar
- human_escalation: explicitly asking for human agent, frustrated, complex issue
- unknown: cannot classify

Respond with JSON: {"intent": "<intent>", "confidence": <0.0-1.0>, "language": "<detected_language_code>", "entities": {}}
Only output the JSON, nothing else."""

RESPONSE_SYSTEM_PROMPT = """You are a helpful, friendly WhatsApp commerce assistant for a small business.
Keep responses concise (under 200 words) — WhatsApp messages should be brief.
Use the customer's language. Be warm but professional.
If you have order/product data, use it. If not, offer to help find it.
Format for WhatsApp: use *bold* for emphasis, line breaks for readability.
Never make up order status or product details — say you'll check if you don't have the data."""

# Template responses when OpenAI is unavailable
FALLBACK_RESPONSES = {
    "order_status": {
        "en": "I'd be happy to help with your order! Could you share your order number? I'll look it up right away. 📦",
        "hi": "मैं आपके ऑर्डर में मदद करना चाहूँगा! क्या आप अपना ऑर्डर नंबर शेयर कर सकते हैं? 📦",
        "pt": "Ficarei feliz em ajudar com seu pedido! Pode compartilhar o número do pedido? 📦",
        "es": "¡Con gusto le ayudo con su pedido! ¿Puede compartir su número de pedido? 📦",
    },
    "product_inquiry": {
        "en": "Thanks for your interest! Let me check that product for you. What specifically would you like to know? 🛍️",
        "hi": "आपकी रुचि के लिए धन्यवाद! मैं उस प्रोडक्ट की जानकारी देता हूँ। आप क्या जानना चाहेंगे? 🛍️",
        "pt": "Obrigado pelo interesse! Deixe-me verificar esse produto. O que gostaria de saber? 🛍️",
        "es": "¡Gracias por su interés! Déjeme verificar ese producto. ¿Qué le gustaría saber? 🛍️",
    },
    "returns": {
        "en": "I understand you'd like to return or exchange an item. Could you share your order number and the reason? I'll guide you through the process. 🔄",
        "hi": "मैं समझता हूँ कि आप कोई आइटम वापस करना चाहते हैं। कृपया अपना ऑर्डर नंबर और कारण बताएं। 🔄",
    },
    "cart_recovery": {
        "en": "Great to see you're back! Your items are still waiting. Ready to complete your purchase? I can help! 🛒",
        "hi": "आपको वापस देखकर खुशी हुई! आपके आइटम अभी भी उपलब्ध हैं। खरीदारी पूरी करें? 🛒",
    },
    "size_guidance": {
        "en": "I can help you find the right size! What product are you looking at, and what are your measurements? 📏",
        "hi": "मैं आपको सही साइज़ खोजने में मदद कर सकता हूँ! कौन सा प्रोडक्ट देख रहे हैं? 📏",
    },
    "payment": {
        "en": "I can help with payment! We support UPI, cards, and other methods. What would you prefer? 💳",
        "hi": "मैं भुगतान में मदद कर सकता हूँ! हम UPI, कार्ड और अन्य तरीकों का समर्थन करते हैं। 💳",
    },
    "greeting": {
        "en": "Hello! 👋 Welcome! How can I help you today?",
        "hi": "नमस्ते! 👋 स्वागत है! आज मैं आपकी कैसे मदद कर सकता हूँ?",
        "pt": "Olá! 👋 Bem-vindo! Como posso ajudá-lo hoje?",
        "es": "¡Hola! 👋 ¡Bienvenido! ¿Cómo puedo ayudarle hoy?",
    },
    "human_escalation": {
        "en": "I understand you'd like to speak with a human agent. Let me connect you right away. Please hold on! 🙋",
        "hi": "मैं समझता हूँ कि आप किसी एजेंट से बात करना चाहते हैं। कृपया प्रतीक्षा करें! 🙋",
    },
    "unknown": {
        "en": "Thanks for your message! Could you tell me more about what you need? I can help with orders, products, returns, and more. 😊",
        "hi": "संदेश के लिए धन्यवाद! कृपया बताएं कि आपको क्या चाहिए? 😊",
    },
}


class AIAgent:
    """Commerce AI Agent powered by GPT-4o-mini."""

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI client: {e}")

    async def classify_intent(self, message: str, conversation_history: list = None) -> dict:
        """Classify customer message intent using GPT-4o-mini."""
        if not self.client:
            return self._fallback_classify(message)

        try:
            messages = [{"role": "system", "content": INTENT_SYSTEM_PROMPT}]
            if conversation_history:
                for h in conversation_history[-5:]:  # Last 5 messages for context
                    messages.append({"role": h.get("role", "user"), "content": h["content"]})
            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=150,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "intent": result.get("intent", "unknown"),
                "confidence": result.get("confidence", 0.5),
                "language": result.get("language", "en"),
                "entities": result.get("entities", {}),
            }
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return self._fallback_classify(message)

    async def generate_response(
        self, intent: str, message: str, language: str = "en",
        context: dict = None, conversation_history: list = None
    ) -> dict:
        """Generate a response using GPT-4o-mini."""
        if not self.client:
            return self._fallback_response(intent, language)

        try:
            context_str = ""
            if context:
                if context.get("order"):
                    o = context["order"]
                    context_str += f"\nOrder #{o.get('id')}: status={o.get('status')}, total={o.get('total')}"
                if context.get("product"):
                    p = context["product"]
                    context_str += f"\nProduct: {p.get('name')}, price={p.get('price')}, in_stock={p.get('inventory_count', 0) > 0}"
                if context.get("business_name"):
                    context_str += f"\nBusiness: {context['business_name']}"

            system = RESPONSE_SYSTEM_PROMPT
            if context_str:
                system += f"\n\nAvailable data:{context_str}"

            messages = [{"role": "system", "content": system}]
            if conversation_history:
                for h in conversation_history[-5:]:
                    messages.append({"role": h.get("role", "user"), "content": h["content"]})
            messages.append({"role": "user", "content": f"[Intent: {intent}] {message}"})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )
            return {
                "text": response.choices[0].message.content,
                "ai_generated": True,
                "model": settings.OPENAI_MODEL,
            }
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._fallback_response(intent, language)

    def _fallback_classify(self, message: str) -> dict:
        """Simple keyword-based fallback classification."""
        msg = message.lower()
        if any(w in msg for w in ["order", "track", "delivery", "ship", "where", "ऑर्डर"]):
            return {"intent": "order_status", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["price", "cost", "available", "stock", "product", "दाम"]):
            return {"intent": "product_inquiry", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["return", "refund", "exchange", "वापस"]):
            return {"intent": "returns", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["size", "fit", "measurement", "साइज़"]):
            return {"intent": "size_guidance", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["pay", "upi", "card", "payment", "भुगतान"]):
            return {"intent": "payment", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["human", "agent", "person", "help", "एजेंट"]):
            return {"intent": "human_escalation", "confidence": 0.6, "language": "en", "entities": {}}
        if any(w in msg for w in ["hi", "hello", "hey", "नमस्ते", "olá", "hola"]):
            return {"intent": "greeting", "confidence": 0.8, "language": "en", "entities": {}}
        return {"intent": "unknown", "confidence": 0.3, "language": "en", "entities": {}}

    def _fallback_response(self, intent: str, language: str) -> dict:
        """Return template response when AI is unavailable."""
        responses = FALLBACK_RESPONSES.get(intent, FALLBACK_RESPONSES["unknown"])
        text = responses.get(language, responses.get("en", "How can I help you?"))
        return {"text": text, "ai_generated": False, "model": "fallback"}


# Singleton
ai_agent = AIAgent()
