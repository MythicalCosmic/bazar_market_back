from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes.health.health import app as health_router
from src.api.routes.v1.auth.admin_auth import router as admin_auth_router
from src.api.routes.v1.admin.users import router as admin_users_router
from src.api.routes.v1.customer.profile import router as customer_profile_router
from src.api.routes.v1.customer.addresses import router as customer_addresses_router
from src.api.middlewares.responseTimeMiddleware import returnResponseTime
from src.core.exceptions import AppException


def create_app() -> FastAPI:
    app = FastAPI(title='Bazar Market Backend', version='1.0')

    # Health
    app.include_router(health_router, prefix='/health', tags=['health'])

    # Admin auth
    app.include_router(admin_auth_router, prefix='/api/v1/auth/admin', tags=['admin-auth'])

    # Admin operations
    app.include_router(admin_users_router, prefix='/api/v1/admin/users', tags=['admin-users'])

    # Customer operations
    app.include_router(customer_profile_router, prefix='/api/v1/customer', tags=['customer-profile'])
    app.include_router(customer_addresses_router, prefix='/api/v1/customer/addresses', tags=['customer-addresses'])

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    returnResponseTime(app)
    return app
