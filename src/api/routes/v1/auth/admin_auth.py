from fastapi import APIRouter, Depends, Header

from src.core.dto.auth import AdminLoginDTO, SessionDTO
from src.core.services.auth_service import AuthService
from src.core.exceptions import ForbiddenException
from src.infrastructure.di import get_auth_service

router = APIRouter()


@router.post("/login", response_model=SessionDTO)
async def admin_login(
    dto: AdminLoginDTO,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.admin_login(dto)


@router.post("/logout")
async def admin_logout(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not authorization.startswith("Bearer "):
        raise ForbiddenException("Invalid authorization header")
    token = authorization[7:]
    await auth_service.logout(token)
    return {"detail": "Logged out"}
