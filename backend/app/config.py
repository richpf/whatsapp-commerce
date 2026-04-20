"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "WhatsApp Commerce Automation"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    API_BASE_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_commerce"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/whatsapp_commerce"

    # Meta WhatsApp Cloud API
    META_WHATSAPP_TOKEN: str = ""
    META_VERIFY_TOKEN: str = "whatsapp-commerce-verify"
    META_PHONE_NUMBER_ID: str = ""
    META_BUSINESS_ACCOUNT_ID: str = ""
    META_APP_SECRET: str = ""
    META_API_VERSION: str = "v21.0"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Shopify
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""

    # WooCommerce (per-seller, but defaults for dev)
    WOOCOMMERCE_URL: str = ""
    WOOCOMMERCE_CONSUMER_KEY: str = ""
    WOOCOMMERCE_CONSUMER_SECRET: str = ""

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_JSON: str = ""

    # Auth
    JWT_SECRET_KEY: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # Rate Limiting
    DEFAULT_RATE_LIMIT_PER_HOUR: int = 100
    DEFAULT_RATE_LIMIT_PER_DAY: int = 1000
    SPAM_SCORE_THRESHOLD: float = 0.7
    QUALITY_SCORE_MIN: float = 0.3

    # Compliance
    MAX_MESSAGES_FREE_TIER: int = 50
    MAX_MESSAGES_STARTER: int = 500
    MAX_MESSAGES_PRO: int = 2000
    MAX_MESSAGES_SCALE: int = 10000

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis (optional, for rate limiting)
    REDIS_URL: Optional[str] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
