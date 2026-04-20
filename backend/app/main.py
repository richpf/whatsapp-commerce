"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.api.webhook import router as webhook_router
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.compliance import router as compliance_router
from app.api.billing import router as billing_router
from app.api.analytics import router as analytics_router
from app.api.catalog import router as catalog_router
from app.api.waitlist import router as waitlist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="WhatsApp-first commerce automation for micro-sellers",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(webhook_router, prefix="/webhook", tags=["WhatsApp Webhook"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(conversations_router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(catalog_router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(waitlist_router, prefix="/api/waitlist", tags=["Waitlist"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/")
async def root():
    return {
        "message": "WhatsApp Commerce Automation API",
        "docs": "/docs",
        "health": "/health",
    }
