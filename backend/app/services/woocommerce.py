"""WooCommerce REST API connector."""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class WooCommerceConnector:
    """Connect to WooCommerce REST API for order/product data."""

    def __init__(self, url: str = "", consumer_key: str = "", consumer_secret: str = ""):
        self.base_url = url.rstrip("/")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def _auth(self):
        return (self.consumer_key, self.consumer_secret)

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/wp-json/wc/v3/{endpoint}"

    async def get_orders(self, limit: int = 50) -> list:
        if not self.consumer_key:
            return self._mock_orders()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("orders"), auth=self._auth(), params={"per_page": limit}
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"WooCommerce get_orders error: {e}")
            return []

    async def get_order(self, order_id: str) -> Optional[dict]:
        if not self.consumer_key:
            return self._mock_order(order_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url(f"orders/{order_id}"), auth=self._auth())
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"WooCommerce get_order error: {e}")
            return None

    async def get_products(self, limit: int = 50) -> list:
        if not self.consumer_key:
            return self._mock_products()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("products"), auth=self._auth(), params={"per_page": limit}
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"WooCommerce get_products error: {e}")
            return []

    async def search_order_by_phone(self, phone: str) -> list:
        if not self.consumer_key:
            return [self._mock_order("2001")]
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self._url("orders"), auth=self._auth(),
                    params={"search": phone, "per_page": 10}
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"WooCommerce search error: {e}")
            return []

    def _mock_orders(self) -> list:
        return [self._mock_order("2001"), self._mock_order("2002")]

    def _mock_order(self, order_id: str) -> dict:
        return {
            "id": order_id,
            "number": order_id,
            "status": "processing",
            "total": "1599.00",
            "currency": "INR",
            "billing": {"first_name": "Test", "last_name": "User", "phone": "+919876543210"},
            "line_items": [{"name": "Organic Cotton T-Shirt", "quantity": 2, "total": "1599.00"}],
        }

    def _mock_products(self) -> list:
        return [
            {"id": "wp1", "name": "Organic Cotton T-Shirt", "price": "799.00",
             "stock_quantity": 25, "images": [{"src": "https://placehold.co/400x400?text=TShirt"}]},
            {"id": "wp2", "name": "Handloom Tote Bag", "price": "599.00",
             "stock_quantity": 12, "images": [{"src": "https://placehold.co/400x400?text=Bag"}]},
        ]
