from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import status, HTTPException
import database_models
from model import ProductBase, ProductUpdate, BulkDeleteRequest
from typing import Optional


def get_all(db: Session, skip: int, limit: int):
    return db.query(database_models.Product).filter(
        database_models.Product.is_active == True
    ).offset(skip).limit(limit).all()


def get_paginated(db: Session, page: int, page_size: int):
    offset = (page - 1) * page_size
    query = db.query(database_models.Product).filter(database_models.Product.is_active == True)
    total = query.count()
    results = query.offset(offset).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total // page_size),  # ceiling division
        "results": results,
    }


def search(
    db: Session,
    name: Optional[str],
    category: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float],
    in_stock: Optional[bool],
    skip: int,
    limit: int,
):
    query = db.query(database_models.Product).filter(database_models.Product.is_active == True)

    if name:
        query = query.filter(database_models.Product.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(database_models.Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(database_models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(database_models.Product.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.filter(database_models.Product.quantity > 0)
        else:
            query = query.filter(database_models.Product.quantity == 0)

    return query.offset(skip).limit(limit).all()


def get_by_id(id: int, db: Session):
    db_product = (
        db.query(database_models.Product)
        .filter(database_models.Product.id == id, database_models.Product.is_active == True)
        .first()
    )
    if db_product:
        return db_product
    raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


def get_by_user(user_id: int, db: Session):
    return (
        db.query(database_models.Product)
        .filter(
            database_models.Product.user_id == user_id,
            database_models.Product.is_active == True,
        )
        .all()
    )


def create(product: ProductBase, db: Session):
    # Verify the user exists
    user = db.query(database_models.Users).filter(database_models.Users.id == product.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {product.user_id} not found")

    new_product = database_models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def update(id: int, product: ProductUpdate, db: Session):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id, database_models.Product.is_active == True
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")

    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete(id: int, db: Session):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id, database_models.Product.is_active == True
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")

    # Soft delete
    db_product.is_active = False
    db.commit()
    return {"detail": f"Product {id} deleted successfully"}


def bulk_delete(request: BulkDeleteRequest, db: Session):
    deleted_count = 0
    not_found_ids = []

    for product_id in request.ids:
        db_product = db.query(database_models.Product).filter(
            database_models.Product.id == product_id,
            database_models.Product.is_active == True,
        ).first()
        if db_product:
            db_product.is_active = False
            deleted_count += 1
        else:
            not_found_ids.append(product_id)

    db.commit()
    return {"deleted_count": deleted_count, "not_found_ids": not_found_ids}


def get_categories(db: Session):
    results = (
        db.query(database_models.Product.category)
        .filter(
            database_models.Product.is_active == True,
            database_models.Product.category.isnot(None),
        )
        .distinct()
        .all()
    )
    return [r[0] for r in results]


def update_stock(id: int, quantity_delta: int, db: Session):
    """Add or subtract from stock quantity. Use negative delta to reduce."""
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id, database_models.Product.is_active == True
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")

    new_qty = db_product.quantity + quantity_delta
    if new_qty < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {db_product.quantity}",
        )
    db_product.quantity = new_qty
    db.commit()
    db.refresh(db_product)
    return db_product
