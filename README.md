# Product Management REST API

A production-ready REST API built with **FastAPI**, **SQLAlchemy**, and **MySQL** featuring JWT authentication, soft deletes, full-text search, and dashboard statistics.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | MySQL (via PyMySQL) |
| Auth | JWT (python-jose + passlib bcrypt) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

## Project Structure

```
├── main.py               # App entry point, middleware, routers
├── database.py           # DB engine & session
├── database_models.py    # SQLAlchemy ORM models
├── model.py              # Pydantic request/response schemas
├── hashing.py            # bcrypt password hashing
├── jwt_token.py          # JWT create / verify / dependency
├── requirements.txt
├── routers/
│   ├── auth.py           # POST /auth/login, GET /auth/me
│   ├── product.py        # Full product CRUD + search + stock
│   ├── user.py           # Full user CRUD + password change
│   └── stats.py          # Dashboard & per-user stats
└── repository/
    ├── products.py       # Product DB operations
    └── users.py          # User DB operations
```

## API Endpoints (20 total)

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login, returns JWT Bearer token |
| GET | `/auth/me` | Get current user profile 🔒 |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product/` | List all products (skip/limit) |
| GET | `/product/paginated` | List with full pagination metadata |
| GET | `/product/search` | Filter by name, category, price, stock |
| GET | `/product/categories` | All distinct categories |
| GET | `/product/{id}` | Get product by ID |
| GET | `/product/user/{user_id}` | All products by a user |
| POST | `/product/` | Create product 🔒 |
| PUT | `/product/{id}` | Update product 🔒 |
| PATCH | `/product/{id}/stock` | Adjust stock quantity (+/-) 🔒 |
| DELETE | `/product/{id}` | Soft-delete product 🔒 |
| DELETE | `/product/bulk` | Bulk soft-delete products 🔒 |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/user/` | Register new user |
| GET | `/user/` | List all users 🔒 |
| GET | `/user/{id}` | Get user with their products |
| PUT | `/user/{id}` | Update name/email 🔒 |
| PATCH | `/user/{id}/change-password` | Change password 🔒 |
| DELETE | `/user/{id}` | Soft-delete user + products 🔒 |

### Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats/dashboard` | System-wide stats 🔒 |
| GET | `/stats/user/{user_id}` | Per-user stats 🔒 |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Basic health check |
| GET | `/health` | Detailed health check |

🔒 = Requires `Authorization: Bearer <token>` header

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create MySQL database
mysql -u root -p -e "CREATE DATABASE python_project;"

# 3. Update DB URL in database.py if needed

# 4. Run the server
uvicorn main:app --reload
```

## Interactive Docs

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Key Design Decisions

- **Soft deletes** — records are never physically removed (`is_active = False`), preserving data integrity
- **Repository pattern** — DB logic separated from route handlers for testability
- **Partial updates** — `PUT` endpoints use `exclude_unset=True` so only sent fields are updated
- **JWT auth** — stateless authentication; token carries user email as subject claim
- **Input validation** — Pydantic validators enforce positive price, non-negative quantity, unique emails
