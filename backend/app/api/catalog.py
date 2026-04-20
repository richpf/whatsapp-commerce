"""Catalog management endpoints."""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Seller
from app.api.auth import get_current_seller
from app.services.catalog import catalog_service

router = APIRouter()


@router.get("/products")
async def list_products(
    category: str = None,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    products = await catalog_service.list_products(db, seller.id, category)
    return {"products": products}


@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    product = await catalog_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products")
async def create_product(
    request: dict,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    if not request.get("name") or not request.get("price"):
        raise HTTPException(status_code=400, detail="Name and price are required")
    product = await catalog_service.create_product(db, seller.id, request)
    return product


@router.patch("/products/{product_id}")
async def update_product(
    product_id: int,
    request: dict,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    product = await catalog_service.update_product(db, product_id, request)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    success = await catalog_service.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}


@router.get("/products/search/{query}")
async def search_products(
    query: str,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    products = await catalog_service.search_products(db, seller.id, query)
    return {"products": products}


@router.post("/products/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV is empty")

    result = await catalog_service.import_csv(db, seller.id, rows)
    return result
