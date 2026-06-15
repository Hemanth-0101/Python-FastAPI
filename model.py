from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
#  Product Schemas
# ─────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    category: Optional[str] = None
    user_id: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


class showProduct(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    category: Optional[str] = None
    user_id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[showProduct]


class BulkDeleteRequest(BaseModel):
    ids: List[int]


class BulkDeleteResponse(BaseModel):
    deleted_count: int
    not_found_ids: List[int]


# ─────────────────────────────────────────────
#  User Schemas
# ─────────────────────────────────────────────

class User(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


class showUser(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: Optional[datetime] = None
    products: List[showProduct] = []

    class Config:
        from_attributes = True


class showUserSummary(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: Optional[datetime] = None
    product_count: int = 0

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
#  Auth Schemas
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# ─────────────────────────────────────────────
#  Stats Schemas
# ─────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    active_products: int
    inactive_products: int
    total_inventory_value: float
    low_stock_products: int          # quantity < 5
    out_of_stock_products: int       # quantity == 0
    categories: List[str]
    top_products: List[showProduct]  # top 5 by price
