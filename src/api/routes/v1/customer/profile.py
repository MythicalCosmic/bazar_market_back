from fastapi import APIRouter, Depends

from src.core.dto.user import CustomerProfileDTO, CustomerProfileUpdateDTO
from src.api.dependencies import get_current_customer
from src.core.services.user_service import UserService
from src.infrastructure.di import get_user_service, get_cache
from src.infrastructure.redis import RedisCache

router = APIRouter()


@router.get("/me", response_model=CustomerProfileDTO)
async def get_my_profile(
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"customer:profile:{user_id}")
    if cached:
        return cached
    user = await service.get_user(user_id)
    profile = CustomerProfileDTO.model_validate(user)
    await cache.set(f"customer:profile:{user_id}", profile.model_dump(), ttl=300)
    return profile


@router.patch("/me", response_model=CustomerProfileDTO)
async def update_my_profile(
    dto: CustomerProfileUpdateDTO,
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.get_user(user_id)
    profile = await service.update_customer_profile(user.telegram_id, dto)
    await cache.delete(f"customer:profile:{user_id}")
    await cache.delete(f"customer:tg:{user.telegram_id}")
    return profile
