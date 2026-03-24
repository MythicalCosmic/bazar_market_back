from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from src.core.dto.user import (
    UserCreateDTO, UserUpdateDTO, UserDTO, UserListDTO,
    AddressCreateDTO, AddressUpdateDTO, AddressDTO,
)
from src.core.enums import UserRole
from src.core.services.user_service import UserService
from src.api.dependencies import get_current_admin, get_cache
from src.infrastructure.di import get_user_service
from src.infrastructure.redis import RedisCache

router = APIRouter()


# ═══════════════════════════════════════════════
#  ADMIN ROUTES — JWT protected, full access
# ═══════════════════════════════════════════════

@router.get("/", response_model=list[UserListDTO])
async def admin_list_users(
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"users:list:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_users(offset=offset, limit=limit)
    await cache.set(f"users:list:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/role/{role}", response_model=list[UserListDTO])
async def admin_list_by_role(
    role: UserRole,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"users:role:{role}:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_by_role(role, offset=offset, limit=limit)
    await cache.set(f"users:role:{role}:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/active", response_model=list[UserListDTO])
async def admin_list_active(
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"users:active:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_active(offset=offset, limit=limit)
    await cache.set(f"users:active:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/count")
async def admin_user_count(
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get("users:count")
    if cached:
        return cached
    count = await service.count_users()
    result = {"count": count}
    await cache.set("users:count", result, ttl=30)
    return result


@router.post("/", response_model=UserDTO, status_code=201)
async def admin_create_user(
    dto: UserCreateDTO,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.create_user(dto)
    await cache.delete_pattern("users:*")
    return user


@router.get("/{user_id}", response_model=UserDTO)
async def admin_get_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return cached
    user = await service.get_user(user_id)
    await cache.set(f"user:{user_id}", user.model_dump(), ttl=120)
    return user


@router.patch("/{user_id}", response_model=UserDTO)
async def admin_update_user(
    user_id: int,
    dto: UserUpdateDTO,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.update_user(user_id, dto)
    await cache.delete(f"user:{user_id}")
    await cache.delete_pattern("users:*")
    return user


@router.delete("/{user_id}")
async def admin_delete_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.delete_user(user_id)
    await cache.delete(f"user:{user_id}")
    await cache.delete_pattern("users:*")
    return {"detail": "User deleted"}


@router.post("/{user_id}/balance")
async def admin_adjust_balance(
    user_id: int,
    amount: Decimal = Query(...),
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    new_balance = await service.adjust_balance(user_id, amount)
    await cache.delete(f"user:{user_id}")
    return {"user_id": user_id, "balance": str(new_balance)}


@router.post("/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.deactivate_user(user_id)
    await cache.delete(f"user:{user_id}")
    await cache.delete_pattern("users:*")
    return {"detail": "User deactivated"}


@router.get("/{user_id}/addresses", response_model=list[AddressDTO])
async def admin_get_user_addresses(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"user:{user_id}:addresses")
    if cached:
        return cached
    addresses = await service.get_addresses(user_id)
    await cache.set(f"user:{user_id}:addresses", [a.model_dump() for a in addresses], ttl=300)
    return addresses
