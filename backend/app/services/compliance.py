"""Compliance Engine: rate limiting, spam scoring, template management, ban-risk alerts."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.models import (
    Seller, Message, ComplianceLog, CostLog, Conversation,
    MessageCategory, PlanTier
)

logger = logging.getLogger(__name__)

# Per-message costs (USD) — Meta 2026 pricing
MESSAGE_COSTS = {
    "marketing": {"IN": 0.0103, "US": 0.025, "BR": 0.0165, "DEFAULT": 0.02},
    "utility": {"IN": 0.0014, "US": 0.004, "BR": 0.0025, "DEFAULT": 0.003},
    "authentication": {"IN": 0.0014, "US": 0.0045, "DEFAULT": 0.003},
    "service": {"IN": 0.0, "US": 0.0, "DEFAULT": 0.0},  # Free within 24hr window
}

PLAN_LIMITS = {
    PlanTier.FREE: 50,
    PlanTier.STARTER: 500,
    PlanTier.PRO: 2000,
    PlanTier.SCALE: 10000,
}

# Safe sending thresholds
RATE_LIMITS = {
    "per_phone_per_hour": 10,  # Max messages to same number per hour
    "per_phone_per_day": 30,
    "new_contacts_per_hour": 50,  # Max new contacts reached per hour
    "total_per_hour": 200,
    "total_per_day": 2000,
}


class ComplianceEngine:
    """Compliance Shield — our core differentiator."""

    async def check_rate_limit(self, db: AsyncSession, seller_id: int,
                                customer_phone: str) -> dict:
        """Check if sending a message would violate rate limits."""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)

        # Messages to this phone in last hour
        phone_hour = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Conversation.customer_phone == customer_phone,
                Message.direction == "outbound",
                Message.created_at >= hour_ago,
            )
        )

        # Messages to this phone in last day
        phone_day = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Conversation.customer_phone == customer_phone,
                Message.direction == "outbound",
                Message.created_at >= day_ago,
            )
        )

        # Total outbound in last hour
        total_hour = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Message.direction == "outbound",
                Message.created_at >= hour_ago,
            )
        )

        violations = []
        if phone_hour >= RATE_LIMITS["per_phone_per_hour"]:
            violations.append(f"Rate limit: {phone_hour} msgs to {customer_phone} in last hour")
        if phone_day >= RATE_LIMITS["per_phone_per_day"]:
            violations.append(f"Rate limit: {phone_day} msgs to {customer_phone} in last 24h")
        if total_hour >= RATE_LIMITS["total_per_hour"]:
            violations.append(f"Rate limit: {total_hour} total msgs in last hour")

        allowed = len(violations) == 0
        if not allowed:
            await self._log_event(db, seller_id, "rate_limit_hit", "warning",
                                   {"violations": violations, "phone": customer_phone})

        return {
            "allowed": allowed,
            "violations": violations,
            "phone_hour": phone_hour,
            "phone_day": phone_day,
            "total_hour": total_hour,
        }

    async def check_plan_limit(self, db: AsyncSession, seller_id: int) -> dict:
        """Check if seller has exceeded their plan's message limit."""
        seller = await db.get(Seller, seller_id)
        if not seller:
            return {"allowed": False, "reason": "Seller not found"}

        current_month = datetime.utcnow().strftime("%Y-%m")
        month_count = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Message.direction == "outbound",
                Message.category != MessageCategory.SERVICE,
                func.to_char(Message.created_at, "YYYY-MM") == current_month,
            )
        ) or 0

        limit = PLAN_LIMITS.get(seller.plan, 50)
        remaining = max(0, limit - month_count)
        usage_pct = (month_count / limit * 100) if limit > 0 else 100

        if usage_pct >= 90 and usage_pct < 100:
            await self._log_event(db, seller_id, "plan_limit_warning", "warning",
                                   {"usage_pct": usage_pct, "count": month_count, "limit": limit})

        return {
            "allowed": month_count < limit,
            "count": month_count,
            "limit": limit,
            "remaining": remaining,
            "usage_pct": round(usage_pct, 1),
        }

    async def calculate_spam_score(self, db: AsyncSession, seller_id: int) -> dict:
        """Calculate spam risk score (0-1) for a seller."""
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)

        # Factors: message volume, block rate, template rejection rate
        outbound_24h = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Message.direction == "outbound",
                Message.created_at >= day_ago,
            )
        ) or 0

        # Unique contacts reached in 24h
        unique_contacts = await db.scalar(
            select(func.count(func.distinct(Conversation.customer_phone)))
            .join(Message, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Message.direction == "outbound",
                Message.created_at >= day_ago,
            )
        ) or 0

        # Marketing message ratio
        marketing_count = await db.scalar(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.seller_id == seller_id,
                Message.direction == "outbound",
                Message.category == MessageCategory.MARKETING,
                Message.created_at >= day_ago,
            )
        ) or 0

        score = 0.0
        factors = []

        # Volume factor
        if outbound_24h > 500:
            score += 0.3
            factors.append("high_volume")
        elif outbound_24h > 200:
            score += 0.15
            factors.append("moderate_volume")

        # Reach factor (too many new contacts)
        if unique_contacts > 100:
            score += 0.25
            factors.append("wide_reach")
        elif unique_contacts > 50:
            score += 0.1
            factors.append("moderate_reach")

        # Marketing ratio
        if outbound_24h > 0:
            marketing_ratio = marketing_count / outbound_24h
            if marketing_ratio > 0.7:
                score += 0.25
                factors.append("high_marketing_ratio")
            elif marketing_ratio > 0.4:
                score += 0.1
                factors.append("moderate_marketing_ratio")

        score = min(score, 1.0)

        if score >= settings.SPAM_SCORE_THRESHOLD:
            await self._log_event(db, seller_id, "spam_alert", "critical",
                                   {"score": score, "factors": factors})

        return {
            "score": round(score, 2),
            "factors": factors,
            "risk_level": "high" if score >= 0.7 else "medium" if score >= 0.4 else "low",
            "outbound_24h": outbound_24h,
            "unique_contacts_24h": unique_contacts,
            "marketing_ratio": round(marketing_count / max(outbound_24h, 1), 2),
        }

    async def calculate_message_cost(self, category: str, country_code: str = "IN") -> float:
        """Calculate per-message cost based on category and country."""
        costs = MESSAGE_COSTS.get(category, MESSAGE_COSTS["service"])
        return costs.get(country_code, costs.get("DEFAULT", 0.0))

    async def log_message_cost(self, db: AsyncSession, seller_id: int,
                                message_id: int, category: str,
                                country_code: str = "IN") -> dict:
        """Log the cost of a sent message."""
        cost_usd = await self.calculate_message_cost(category, country_code)
        cost_inr = cost_usd * 83.5  # Approximate USD/INR

        cost_log = CostLog(
            seller_id=seller_id,
            message_id=message_id,
            category=MessageCategory(category) if category in MessageCategory.__members__.values() else MessageCategory.SERVICE,
            cost_usd=cost_usd,
            cost_inr=cost_inr,
            month=datetime.utcnow().strftime("%Y-%m"),
        )
        db.add(cost_log)
        return {"cost_usd": cost_usd, "cost_inr": cost_inr}

    async def get_monthly_costs(self, db: AsyncSession, seller_id: int,
                                 month: Optional[str] = None) -> dict:
        """Get monthly cost breakdown by category."""
        if not month:
            month = datetime.utcnow().strftime("%Y-%m")

        results = await db.execute(
            select(CostLog.category, func.sum(CostLog.cost_usd), func.count(CostLog.id))
            .where(CostLog.seller_id == seller_id, CostLog.month == month)
            .group_by(CostLog.category)
        )

        breakdown = {}
        total_usd = 0.0
        total_messages = 0
        for row in results:
            cat = row[0].value if hasattr(row[0], 'value') else str(row[0])
            cost = float(row[1] or 0)
            count = int(row[2] or 0)
            breakdown[cat] = {"cost_usd": round(cost, 4), "messages": count}
            total_usd += cost
            total_messages += count

        return {
            "month": month,
            "total_usd": round(total_usd, 4),
            "total_inr": round(total_usd * 83.5, 2),
            "total_messages": total_messages,
            "breakdown": breakdown,
        }

    async def get_ban_risk_assessment(self, db: AsyncSession, seller_id: int) -> dict:
        """Comprehensive ban risk assessment."""
        spam = await self.calculate_spam_score(db, seller_id)
        rate = await self.check_rate_limit(db, seller_id, "")  # General check
        plan = await self.check_plan_limit(db, seller_id)

        risk_factors = []
        risk_level = "low"

        if spam["score"] >= 0.7:
            risk_factors.append("High spam score — reduce marketing messages")
            risk_level = "critical"
        elif spam["score"] >= 0.4:
            risk_factors.append("Moderate spam score — monitor messaging patterns")
            risk_level = "medium"

        if plan.get("usage_pct", 0) >= 90:
            risk_factors.append("Approaching plan message limit")

        recommendations = []
        if "high_volume" in spam["factors"]:
            recommendations.append("Reduce daily message volume below 500")
        if "wide_reach" in spam["factors"]:
            recommendations.append("Limit new contacts to under 100/day")
        if "high_marketing_ratio" in spam["factors"]:
            recommendations.append("Balance marketing with utility/service messages")
        if not recommendations:
            recommendations.append("Your messaging patterns look healthy!")

        return {
            "risk_level": risk_level,
            "spam_score": spam["score"],
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "plan_usage": plan,
        }

    async def track_opt_in(self, db: AsyncSession, seller_id: int,
                            customer_phone: str, opted_in: bool) -> None:
        """Track customer opt-in/opt-out status."""
        conv = await db.execute(
            select(Conversation).where(
                Conversation.seller_id == seller_id,
                Conversation.customer_phone == customer_phone,
            )
        )
        conversation = conv.scalar_one_or_none()
        if conversation:
            conversation.is_opted_in = opted_in
            if opted_in:
                conversation.opted_in_at = datetime.utcnow()

        event_type = "opt_in" if opted_in else "opt_out"
        await self._log_event(db, seller_id, event_type, "info",
                               {"phone": customer_phone})

    async def _log_event(self, db: AsyncSession, seller_id: int,
                          event_type: str, severity: str, details: dict,
                          message_id: int = None) -> None:
        log = ComplianceLog(
            seller_id=seller_id,
            event_type=event_type,
            severity=severity,
            details=details,
            message_id=message_id,
        )
        db.add(log)


# Singleton
compliance_engine = ComplianceEngine()
