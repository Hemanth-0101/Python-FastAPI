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

## Prerequisites

- Python **3.12** (avoid 3.14 — it has compatibility issues with some dependencies)
- MySQL **8.x**
- Git

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 2. Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create MySQL database
mysql -u root -p -e "CREATE DATABASE python_project;"

# 5. Update DB credentials in database.py if needed
# Default: mysql+pymysql://root:root@localhost:3306/python_project

# 6. Run the server
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

## Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Design Decisions

- **Soft deletes** — records are never physically removed (`is_active = False`), preserving data integrity
- **Repository pattern** — DB logic separated from route handlers for testability
- **Partial updates** — `PUT` endpoints use `exclude_unset=True` so only sent fields are updated
- **JWT auth** — stateless authentication; token carries user email as subject claim
- **Input validation** — Pydantic validators enforce positive price, non-negative quantity, unique emails

## Troubleshooting

**MySQL connection error** — Verify MySQL is running and credentials in `database.py` match your local setup.

**bcrypt / passlib warning** — If you see a "password cannot be longer than 72 bytes" error, pin the version and restart the server:
```bash
pip install bcrypt==4.0.1 passlib[bcrypt]==1.7.4
uvicorn main:app --reload
```