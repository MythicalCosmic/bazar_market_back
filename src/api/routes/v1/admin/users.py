from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from src.core.dto.user import (
    UserCreateDTO, UserUpdateDTO, UserDTO, UserListDTO,
    AdminCreateDTO, AddressDTO,
)
from src.core.enums import UserRole, AdminPermission
from src.core.services.user_service import UserService
from src.core.services.auth_service import AuthService
from src.api.dependencies import require_permission
from src.infrastructure.di import get_user_service, get_auth_service, get_cache
from src.infrastructure.redis import RedisCache

router = APIRouter()


# ── List / Filter / Stats ──

@router.get("/", response_model=list[UserListDTO])
async def list_users(
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"admin:users:list:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_users(offset=offset, limit=limit)
    await cache.set(f"admin:users:list:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/role/{role}", response_model=list[UserListDTO])
async def list_by_role(
    role: UserRole,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"admin:users:role:{role}:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_by_role(role, offset=offset, limit=limit)
    await cache.set(f"admin:users:role:{role}:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/active", response_model=list[UserListDTO])
async def list_active(
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    cached = await cache.get(f"admin:users:active:{offset}:{limit}")
    if cached:
        return cached
    users = await service.list_active(offset=offset, limit=limit)
    await cache.set(f"admin:users:active:{offset}:{limit}", [u.model_dump() for u in users], ttl=60)
    return users


@router.get("/count")
async def user_count(
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get("admin:users:count")
    if cached:
        return cached
    count = await service.count_users()
    result = {"count": count}
    await cache.set("admin:users:count", result, ttl=30)
    return result


# ── Create ──

@router.post("/", response_model=UserDTO, status_code=201)
async def create_user(
    dto: UserCreateDTO,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_CREATE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.create_user(dto)
    await cache.delete_pattern("admin:users:*")
    return user


@router.post("/admin", response_model=UserDTO, status_code=201)
async def create_admin(
    dto: AdminCreateDTO,
    _: UserDTO = Depends(require_permission(AdminPermission.ADMINS_MANAGE)),
    service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    cache: RedisCache = Depends(get_cache),
):
    password_hash = auth_service.hash_password(dto.password)
    user = await service.create_admin(dto, password_hash)
    await cache.delete_pattern("admin:users:*")
    return user


# ── Get / Update / Delete ──

@router.get("/{user_id}", response_model=UserDTO)
async def get_user(
    user_id: int,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"admin:user:{user_id}")
    if cached:
        return cached
    user = await service.get_user(user_id)
    await cache.set(f"admin:user:{user_id}", user.model_dump(), ttl=120)
    return user


@router.patch("/{user_id}", response_model=UserDTO)
async def update_user(
    user_id: int,
    dto: UserUpdateDTO,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_UPDATE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.update_user(user_id, dto)
    await cache.delete(f"admin:user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("admin:users:*")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_DELETE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.delete_user(user_id)
    await cache.delete(f"admin:user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("admin:users:*")
    return {"detail": "User deleted"}


# ── Actions ──

@router.post("/{user_id}/balance")
async def adjust_balance(
    user_id: int,
    amount: Decimal = Query(...),
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_BALANCE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    new_balance = await service.adjust_balance(user_id, amount)
    await cache.delete(f"admin:user:{user_id}")
    return {"user_id": user_id, "balance": str(new_balance)}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_DELETE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.deactivate_user(user_id)
    await cache.delete(f"admin:user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    await cache.delete_pattern("admin:users:*")
    return {"detail": "User deactivated"}


@router.post("/{user_id}/verify")
async def verify_user(
    user_id: int,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VERIFY)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    await service.verify_user(user_id)
    await cache.delete(f"admin:user:{user_id}")
    await cache.delete_pattern("admin:users:*")
    return {"detail": "User verified"}


@router.put("/{user_id}/permissions", response_model=UserDTO)
async def update_permissions(
    user_id: int,
    permissions: list[str],
    _: UserDTO = Depends(require_permission(AdminPermission.ADMINS_MANAGE)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    user = await service.update_permissions(user_id, permissions)
    await cache.delete(f"admin:user:{user_id}")
    await cache.delete(f"admin:session:{user_id}")
    return user


# ── Addresses (admin view) ──

@router.get("/{user_id}/addresses", response_model=list[AddressDTO])
async def get_user_addresses(
    user_id: int,
    _: UserDTO = Depends(require_permission(AdminPermission.USERS_VIEW)),
    service: UserService = Depends(get_user_service),
    cache: RedisCache = Depends(get_cache),
):
    cached = await cache.get(f"admin:user:{user_id}:addresses")
    if cached:
        return cached
    addresses = await service.get_addresses(user_id)
    await cache.set(f"admin:user:{user_id}:addresses", [a.model_dump() for a in addresses], ttl=300)
    return addresses
