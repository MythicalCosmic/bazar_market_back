from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from src.core.dto.user import (
    UserCreateDTO, UserUpdateDTO, UserDTO, UserListDTO,
    AdminCreateDTO, AddressDTO,
)
from src.core.enums import UserRole
from src.core.services.user_service import UserService
from src.core.services.auth_service import AuthService
from src.api.dependencies import get_current_admin
from src.infrastructure.di import get_user_service, get_auth_service, get_cache
from src.infrastructure.redis import RedisCache

router = APIRouter()


# ── List / Filter / Search ──

@router.get("/", response_model=list[UserListDTO])
async def list_users(
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
async def list_by_role(
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
async def list_active(
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
async def user_count(
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


# ── Create ──

@router.post("/", response_model=UserDTO, status_code=201)
async def create_user(
    dto: UserCreateDTO,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.create_user(dto)
    await cache.delete_pattern("users:*")
    return user


@router.post("/admin", response_model=UserDTO, status_code=201)
async def create_admin(
    dto: AdminCreateDTO,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    cache: RedisCache = Depends(get_cache),
):
    password_hash = auth_service.hash_password(dto.password)
    user = await service.create_admin(dto, password_hash)
    await cache.delete_pattern("users:*")
    return user


# ── Get / Update / Delete ──

@router.get("/{user_id}", response_model=UserDTO)
async def get_user(
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
async def update_user(
    user_id: int,
    dto: UserUpdateDTO,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.update_user(user_id, dto)
    await cache.delete(f"user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("users:*")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.delete_user(user_id)
    await cache.delete(f"user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("users:*")
    return {"detail": "User deleted"}


# ── Actions ──

@router.post("/{user_id}/balance")
async def adjust_balance(
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
async def deactivate_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.deactivate_user(user_id)
    await cache.delete(f"user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("users:*")
    return {"detail": "User deactivated"}


@router.post("/{user_id}/verify")
async def verify_user(
    user_id: int,
    _: UserDTO = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.verify_user(user_id)
    await cache.delete(f"user:{user_id}")
    await cache.delete_pattern("users:*")
    return {"detail": "User verified"}


# ── Addresses ──

@router.get("/{user_id}/addresses", response_model=list[AddressDTO])
async def get_user_addresses(
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
