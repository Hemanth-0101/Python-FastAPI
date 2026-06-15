from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import database_models
from database import engine
from routers.product import router as product_router
from routers.user import router as user_router
from routers.auth import router as auth_router
from routers.stats import router as stats_router

# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Product Management API",
    description=(
        "A RESTful API built with FastAPI, SQLAlchemy, and MySQL.\n\n"
        "Features:\n"
        "- JWT Authentication\n"
        "- Full CRUD for Users and Products\n"
        "- Search & filter, pagination\n"
        "- Soft deletes\n"
        "- Stock management\n"
        "- Dashboard statistics\n"
    ),
    version="1.0.0",
    contact={"name": "Hemanth"},
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )

# ── DB init ───────────────────────────────────────────────────────────────────
database_models.Base.metadata.create_all(bind=engine)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(stats_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "message": "Product Management API is running"}


@app.get("/health", tags=["Health"], summary="Detailed health check")
def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
    }
