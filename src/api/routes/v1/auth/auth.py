from fastapi import APIRouter, Depends

from src.core.dto.auth import AdminLoginDTO, TokenDTO, RefreshDTO
from src.core.services.auth_service import AuthService
from src.infrastructure.di import get_auth_service

router = APIRouter()


@router.post("/admin/login", response_model=TokenDTO)
async def admin_login(
    dto: AdminLoginDTO,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.admin_login(dto)


@router.post("/admin/refresh", response_model=TokenDTO)
async def admin_refresh(
    dto: RefreshDTO,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_tokens(dto.refresh_token)
