from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes.health.health import app as health_router
from src.api.routes.v1.auth.auth import router as auth_router
from src.api.routes.v1.users.users import router as users_router
from src.api.middlewares.responseTimeMiddleware import returnResponseTime
from src.core.exceptions import AppException


def create_app() -> FastAPI:
    app = FastAPI(title='Bazar Market Backend', version='1.0')

    app.include_router(health_router, prefix='/health', tags=['health'])
    app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])
    app.include_router(users_router, prefix='/api/v1/users', tags=['users'])

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    returnResponseTime(app)
    return app
