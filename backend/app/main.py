from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.admin_routes import router as admin_router
from app.api.auth_routes import router as auth_router
from app.api.crm_routes import router as crm_router
from app.core.config import settings

app = FastAPI(title="QHI AUTO API", version="0.1.0", description="EV import catalog and quotation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
)
app.include_router(router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(crm_router, prefix="/api/v1")
