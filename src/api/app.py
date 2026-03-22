from fastapi import FastAPI
from src.api.routes.health.health import app as health_router


def create_app() -> FastAPI:
    app = FastAPI(title='Bazar Market Backend', version='1.0')
    app.include_router(health_router, prefix='/health', tags=['health'])
    return app
