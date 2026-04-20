"""SQLAlchemy models for WhatsApp Commerce."""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, Enum, JSON, Index, BigInteger
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), default="landing_page")
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlanTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    SCALE = "scale"


class StoreType(str, enum.Enum):
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    GOOGLE_SHEETS = "google_sheets"
    CSV = "csv"
    MANUAL = "manual"


class MessageCategory(str, enum.Enum):
    MARKETING = "marketing"
    UTILITY = "utility"
    AUTHENTICATION = "authentication"
    SERVICE = "service"


class TemplateStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class IntentType(str, enum.Enum):
    ORDER_STATUS = "order_status"
    PRODUCT_INQUIRY = "product_inquiry"
    RETURNS = "returns"
    CART_RECOVERY = "cart_recovery"
    SIZE_GUIDANCE = "size_guidance"
    PAYMENT = "payment"
    GREETING = "greeting"
    HUMAN_ESCALATION = "human_escalation"
    UNKNOWN = "unknown"


# ─── Seller ───────────────────────────────────────────────────────────────────

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)
    business_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    whatsapp_phone_id = Column(String(100), nullable=True)
    whatsapp_business_id = Column(String(100), nullable=True)
    meta_access_token = Column(Text, nullable=True)
    plan = Column(Enum(PlanTier), default=PlanTier.FREE, nullable=False)
    store_type = Column(Enum(StoreType), nullable=True)
    store_config = Column(JSON, nullable=True)  # Store-specific credentials/config
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="Asia/Kolkata")
    setup_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="seller")
    products = relationship("Product", back_populates="seller")
    templates = relationship("Template", back_populates="seller")
    compliance_logs = relationship("ComplianceLog", back_populates="seller")
    cost_logs = relationship("CostLog", back_populates="seller")
    orders = relationship("Order", back_populates="seller")


# ─── Conversation ─────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(255), nullable=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    language = Column(String(10), default="en")
    last_message_at = Column(DateTime, nullable=True)
    ai_confidence_avg = Column(Float, nullable=True)
    is_opted_in = Column(Boolean, default=False)
    opted_in_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("Seller", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

    __table_args__ = (
        Index("ix_conv_seller_customer", "seller_id", "customer_phone"),
    )


# ─── Message ──────────────────────────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # "inbound" or "outbound"
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, template, interactive
    category = Column(Enum(MessageCategory), nullable=True)
    intent = Column(Enum(IntentType), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_generated = Column(Boolean, default=False)
    template_name = Column(String(255), nullable=True)
    meta_message_id = Column(String(255), nullable=True)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


# ─── Product (Built-in Catalog) ──────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    external_id = Column(String(255), nullable=True)  # Shopify/WooCommerce product ID
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    image_url = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    inventory_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    variants = Column(JSON, nullable=True)  # Size, color, etc.
    source = Column(Enum(StoreType), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("Seller", back_populates="products")


# ─── Order ────────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    external_order_id = Column(String(255), nullable=True)
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(255), nullable=True)
    items = Column(JSON, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(String(50), default="pending")  # pending, confirmed, shipped, delivered, cancelled, returned
    payment_status = Column(String(50), default="unpaid")  # unpaid, paid, refunded
    payment_method = Column(String(50), nullable=True)
    payment_link = Column(Text, nullable=True)
    tracking_number = Column(String(255), nullable=True)
    tracking_url = Column(Text, nullable=True)
    source = Column(Enum(StoreType), nullable=True)
    cart_abandoned = Column(Boolean, default=False)
    cart_recovered = Column(Boolean, default=False)
    recovery_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("Seller", back_populates="orders")


# ─── Template ─────────────────────────────────────────────────────────────────

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    language = Column(String(10), default="en")
    category = Column(Enum(MessageCategory), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # List of variable placeholders
    status = Column(Enum(TemplateStatus), default=TemplateStatus.PENDING)
    meta_template_id = Column(String(255), nullable=True)
    is_festival = Column(Boolean, default=False)
    festival_name = Column(String(100), nullable=True)
    uses_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("Seller", back_populates="templates")


# ─── Compliance Log ──────────────────────────────────────────────────────────

class ComplianceLog(Base):
    __tablename__ = "compliance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # rate_limit_hit, spam_alert, quality_drop, ban_risk, opt_in, opt_out
    severity = Column(String(20), default="info")  # info, warning, critical
    details = Column(JSON, nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("Seller", back_populates="compliance_logs")


# ─── Cost Log ─────────────────────────────────────────────────────────────────

class CostLog(Base):
    __tablename__ = "cost_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    category = Column(Enum(MessageCategory), nullable=False)
    cost_usd = Column(Float, nullable=False)
    cost_inr = Column(Float, nullable=True)
    month = Column(String(7), nullable=False)  # YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("Seller", back_populates="cost_logs")

    __table_args__ = (
        Index("ix_cost_seller_month", "seller_id", "month"),
    )
