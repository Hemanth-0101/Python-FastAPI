from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import database, database_models
from model import DashboardStats
from jwt_token import get_current_user

router = APIRouter(prefix="/stats", tags=["Dashboard & Stats"])


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get overall system stats (requires auth)",
)
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    total_users = db.query(database_models.Users).filter(database_models.Users.is_active == True).count()
    total_products = db.query(database_models.Product).filter(database_models.Product.is_active == True).count()
    active_products = total_products  # is_active == True already filtered above
    inactive_products = db.query(database_models.Product).filter(database_models.Product.is_active == False).count()

    inventory_value_result = (
        db.query(func.sum(database_models.Product.price * database_models.Product.quantity))
        .filter(database_models.Product.is_active == True)
        .scalar()
    )
    total_inventory_value = float(inventory_value_result or 0)

    low_stock = db.query(database_models.Product).filter(
        database_models.Product.is_active == True,
        database_models.Product.quantity > 0,
        database_models.Product.quantity < 5,
    ).count()

    out_of_stock = db.query(database_models.Product).filter(
        database_models.Product.is_active == True,
        database_models.Product.quantity == 0,
    ).count()

    category_rows = (
        db.query(database_models.Product.category)
        .filter(
            database_models.Product.is_active == True,
            database_models.Product.category.isnot(None),
        )
        .distinct()
        .all()
    )
    categories = [r[0] for r in category_rows]

    top_products = (
        db.query(database_models.Product)
        .filter(database_models.Product.is_active == True)
        .order_by(database_models.Product.price.desc())
        .limit(5)
        .all()
    )

    return DashboardStats(
        total_users=total_users,
        total_products=total_products,
        active_products=active_products,
        inactive_products=inactive_products,
        total_inventory_value=total_inventory_value,
        low_stock_products=low_stock,
        out_of_stock_products=out_of_stock,
        categories=categories,
        top_products=top_products,
    )


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Get product stats for a specific user (requires auth)",
)
def get_user_stats(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    user = db.query(database_models.Users).filter(
        database_models.Users.id == user_id, database_models.Users.is_active == True
    ).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    product_count = db.query(database_models.Product).filter(
        database_models.Product.user_id == user_id,
        database_models.Product.is_active == True,
    ).count()

    value = (
        db.query(func.sum(database_models.Product.price * database_models.Product.quantity))
        .filter(
            database_models.Product.user_id == user_id,
            database_models.Product.is_active == True,
        )
        .scalar()
    )

    return {
        "user_id": user_id,
        "user_name": user.name,
        "product_count": product_count,
        "total_inventory_value": float(value or 0),
    }
