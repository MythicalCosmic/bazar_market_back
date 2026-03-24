from fastapi import APIRouter, Depends

from src.core.dto.user import AddressCreateDTO, AddressUpdateDTO, AddressDTO
from src.api.dependencies import get_current_customer
from src.core.services.user_service import UserService
from src.infrastructure.di import get_user_service, get_cache
from src.infrastructure.redis import RedisCache

router = APIRouter()


@router.get("/", response_model=list[AddressDTO])
async def list_my_addresses(
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"customer:addresses:{user_id}")
    if cached:
        return cached
    addresses = await service.get_addresses(user_id)
    await cache.set(f"customer:addresses:{user_id}", [a.model_dump() for a in addresses], ttl=300)
    return addresses


@router.post("/", response_model=AddressDTO, status_code=201)
async def create_address(
    dto: AddressCreateDTO,
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    address = await service.create_address(user_id, dto)
    await cache.delete(f"customer:addresses:{user_id}")
    return address


@router.patch("/{address_id}", response_model=AddressDTO)
async def update_address(
    address_id: int,
    dto: AddressUpdateDTO,
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    address = await service.update_address(user_id, address_id, dto)
    await cache.delete(f"customer:addresses:{user_id}")
    return address


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.delete_address(address_id)
    await cache.delete(f"customer:addresses:{user_id}")
    return {"detail": "Address deleted"}


@router.get("/default", response_model=AddressDTO | None)
async def get_default_address(
    user_id: int = Depends(get_current_customer),
    service: UserService = Depends(get_user_service),
):
    return await service.get_default_address(user_id)
