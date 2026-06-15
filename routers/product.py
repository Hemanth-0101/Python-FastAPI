from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import database
from model import ProductBase, ProductUpdate, showProduct, PaginatedProducts, BulkDeleteRequest, BulkDeleteResponse
from repository import products
from jwt_token import get_current_user
import database_models

router = APIRouter(prefix="/product", tags=["Products"])


# ── READ ──────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[showProduct],
    status_code=status.HTTP_200_OK,
    summary="List all active products (simple, with skip/limit)",
)
def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(database.get_db),
):
    return products.get_all(db, skip, limit)


@router.get(
    "/paginated",
    response_model=PaginatedProducts,
    status_code=status.HTTP_200_OK,
    summary="List products with full pagination metadata",
)
def get_products_paginated(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(database.get_db),
):
    return products.get_paginated(db, page, page_size)


@router.get(
    "/search",
    response_model=List[showProduct],
    status_code=status.HTTP_200_OK,
    summary="Search and filter products",
)
def search_products(
    name: Optional[str] = Query(None, description="Partial name match (case-insensitive)"),
    category: Optional[str] = Query(None, description="Partial category match"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: Optional[bool] = Query(None, description="True = quantity > 0"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(database.get_db),
):
    return products.search(db, name, category, min_price, max_price, in_stock, skip, limit)


@router.get(
    "/categories",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get all distinct product categories",
)
def get_categories(db: Session = Depends(database.get_db)):
    return products.get_categories(db)


@router.get(
    "/user/{user_id}",
    response_model=List[showProduct],
    status_code=status.HTTP_200_OK,
    summary="Get all active products belonging to a specific user",
)
def get_products_by_user(user_id: int, db: Session = Depends(database.get_db)):
    return products.get_by_user(user_id, db)


@router.get(
    "/{id}",
    response_model=showProduct,
    status_code=status.HTTP_200_OK,
    summary="Get a single product by ID",
)
def get_product_by_id(id: int, db: Session = Depends(database.get_db)):
    return products.get_by_id(id, db)


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=showProduct,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product (requires auth)",
)
def create_product(
    product: ProductBase,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return products.create(product, db)


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put(
    "/{id}",
    response_model=showProduct,
    status_code=status.HTTP_200_OK,
    summary="Full update of a product (requires auth)",
)
def update_product(
    id: int,
    product: ProductUpdate,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return products.update(id, product, db)


@router.patch(
    "/{id}/stock",
    response_model=showProduct,
    status_code=status.HTTP_200_OK,
    summary="Adjust stock quantity by a delta (+ to add, - to subtract)",
)
def update_stock(
    id: int,
    quantity_delta: int = Query(..., description="Amount to add (positive) or remove (negative)"),
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return products.update_stock(id, quantity_delta, db)


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete(
    "/bulk",
    response_model=BulkDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete multiple products by ID list (requires auth)",
)
def bulk_delete_products(
    request: BulkDeleteRequest,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return products.bulk_delete(request, db)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a product by ID (requires auth)",
)
def delete_product(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return products.delete(id, db)
