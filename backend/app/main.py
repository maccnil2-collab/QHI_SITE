import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.admin_routes import router as admin_router
from app.api.auth_routes import router as auth_router
from app.api.crm_routes import router as crm_router
from app.core.config import settings

def create_app(environment: str | None = None) -> FastAPI:
    production = (environment or os.getenv("APP_ENV", "development")).lower() == "production"
    application = FastAPI(
        title="QHI AUTO API",
        version="0.1.0",
        description="EV import catalog and quotation API",
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )

    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Admin-Token", "X-File-Name"],
    )
    application.include_router(router, prefix="/api/v1")
    application.include_router(admin_router, prefix="/api/v1")
    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(crm_router, prefix="/api/v1")
    return application


app = create_app()
