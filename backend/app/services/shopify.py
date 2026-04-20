"""Shopify Admin API connector."""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class ShopifyConnector:
    """Connect to Shopify Admin API for order/product data."""

    def __init__(self, shop_url: str = "", access_token: str = ""):
        self.shop_url = shop_url.rstrip("/")
        self.access_token = access_token
        self.api_version = "2024-10"

    def _headers(self):
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    def _url(self, endpoint: str) -> str:
        return f"https://{self.shop_url}/admin/api/{self.api_version}/{endpoint}.json"

    async def get_orders(self, limit: int = 50, status: str = "any") -> list:
        """Fetch recent orders."""
        if not self.access_token:
            return self._mock_orders()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("orders"),
                    headers=self._headers(),
                    params={"limit": limit, "status": status},
                )
                resp.raise_for_status()
                return resp.json().get("orders", [])
        except Exception as e:
            logger.error(f"Shopify get_orders error: {e}")
            return []

    async def get_order(self, order_id: str) -> Optional[dict]:
        """Fetch a single order by ID."""
        if not self.access_token:
            return self._mock_order(order_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url(f"orders/{order_id}"), headers=self._headers())
                resp.raise_for_status()
                return resp.json().get("order")
        except Exception as e:
            logger.error(f"Shopify get_order error: {e}")
            return None

    async def get_products(self, limit: int = 50) -> list:
        """Fetch products."""
        if not self.access_token:
            return self._mock_products()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("products"), headers=self._headers(), params={"limit": limit}
                )
                resp.raise_for_status()
                return resp.json().get("products", [])
        except Exception as e:
            logger.error(f"Shopify get_products error: {e}")
            return []

    async def get_product(self, product_id: str) -> Optional[dict]:
        """Fetch a single product."""
        if not self.access_token:
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url(f"products/{product_id}"), headers=self._headers()
                )
                resp.raise_for_status()
                return resp.json().get("product")
        except Exception as e:
            logger.error(f"Shopify get_product error: {e}")
            return None

    async def search_order_by_phone(self, phone: str) -> list:
        """Search orders by customer phone number."""
        if not self.access_token:
            return [self._mock_order("1001")]
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("orders"),
                    headers=self._headers(),
                    params={"status": "any", "limit": 10},
                )
                resp.raise_for_status()
                orders = resp.json().get("orders", [])
                return [o for o in orders if phone in str(o.get("phone", ""))
                        or phone in str(o.get("customer", {}).get("phone", ""))]
        except Exception as e:
            logger.error(f"Shopify search error: {e}")
            return []

    def _mock_orders(self) -> list:
        return [
            self._mock_order("1001"),
            self._mock_order("1002"),
        ]

    def _mock_order(self, order_id: str) -> dict:
        return {
            "id": order_id,
            "order_number": f"#{order_id}",
            "financial_status": "paid",
            "fulfillment_status": "shipped",
            "total_price": "1299.00",
            "currency": "INR",
            "created_at": "2026-04-18T10:30:00+05:30",
            "customer": {"first_name": "Test", "last_name": "Customer", "phone": "+919876543210"},
            "line_items": [{"title": "Cotton Kurta - Blue (M)", "quantity": 1, "price": "1299.00"}],
            "tracking_number": "TRACK123456",
            "tracking_url": "https://track.example.com/TRACK123456",
        }

    def _mock_products(self) -> list:
        return [
            {"id": "p1", "title": "Cotton Kurta - Blue", "variants": [{"price": "1299.00", "inventory_quantity": 15}],
             "images": [{"src": "https://placehold.co/400x400?text=Kurta"}]},
            {"id": "p2", "title": "Silver Jhumka Earrings", "variants": [{"price": "899.00", "inventory_quantity": 8}],
             "images": [{"src": "https://placehold.co/400x400?text=Earrings"}]},
            {"id": "p3", "title": "Hand-painted Silk Scarf", "variants": [{"price": "2499.00", "inventory_quantity": 3}],
             "images": [{"src": "https://placehold.co/400x400?text=Scarf"}]},
        ]
