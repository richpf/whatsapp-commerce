"""Built-in lightweight catalog for sellers without Shopify/WooCommerce."""

import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Product, StoreType

logger = logging.getLogger(__name__)


class CatalogService:
    """Manage built-in product catalog."""

    async def list_products(self, db: AsyncSession, seller_id: int,
                            category: str = None, active_only: bool = True) -> list:
        query = select(Product).where(Product.seller_id == seller_id)
        if active_only:
            query = query.where(Product.is_active == True)
        if category:
            query = query.where(Product.category == category)
        query = query.order_by(Product.name)
        result = await db.execute(query)
        return [self._to_dict(p) for p in result.scalars().all()]

    async def get_product(self, db: AsyncSession, product_id: int) -> Optional[dict]:
        product = await db.get(Product, product_id)
        return self._to_dict(product) if product else None

    async def create_product(self, db: AsyncSession, seller_id: int, data: dict) -> dict:
        product = Product(
            seller_id=seller_id,
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            currency=data.get("currency", "INR"),
            image_url=data.get("image_url"),
            category=data.get("category"),
            inventory_count=data.get("inventory_count", 0),
            variants=data.get("variants"),
            source=StoreType.MANUAL,
        )
        db.add(product)
        await db.flush()
        return self._to_dict(product)

    async def update_product(self, db: AsyncSession, product_id: int, data: dict) -> Optional[dict]:
        product = await db.get(Product, product_id)
        if not product:
            return None
        for key in ["name", "description", "price", "currency", "image_url",
                     "category", "inventory_count", "variants", "is_active"]:
            if key in data:
                setattr(product, key, data[key])
        await db.flush()
        return self._to_dict(product)

    async def delete_product(self, db: AsyncSession, product_id: int) -> bool:
        product = await db.get(Product, product_id)
        if not product:
            return False
        await db.delete(product)
        return True

    async def search_products(self, db: AsyncSession, seller_id: int, query: str) -> list:
        result = await db.execute(
            select(Product).where(
                Product.seller_id == seller_id,
                Product.is_active == True,
                Product.name.ilike(f"%{query}%"),
            )
        )
        return [self._to_dict(p) for p in result.scalars().all()]

    async def import_csv(self, db: AsyncSession, seller_id: int, rows: list) -> dict:
        """Import products from CSV rows (list of dicts)."""
        created = 0
        errors = []
        for i, row in enumerate(rows):
            try:
                await self.create_product(db, seller_id, {
                    "name": row.get("name") or row.get("Name", ""),
                    "description": row.get("description") or row.get("Description", ""),
                    "price": float(row.get("price") or row.get("Price", 0)),
                    "currency": row.get("currency") or row.get("Currency", "INR"),
                    "image_url": row.get("image_url") or row.get("Image URL", ""),
                    "category": row.get("category") or row.get("Category", ""),
                    "inventory_count": int(row.get("inventory_count") or row.get("Stock", 0)),
                })
                created += 1
            except Exception as e:
                errors.append({"row": i, "error": str(e)})
        return {"created": created, "errors": errors}

    def _to_dict(self, product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "currency": product.currency,
            "image_url": product.image_url,
            "category": product.category,
            "inventory_count": product.inventory_count,
            "is_active": product.is_active,
            "variants": product.variants,
            "source": product.source.value if product.source else None,
            "created_at": product.created_at.isoformat() if product.created_at else None,
        }


catalog_service = CatalogService()
