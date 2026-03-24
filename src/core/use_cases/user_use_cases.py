from decimal import Decimal

from src.core.dto.user import (
    UserCreateDTO, UserUpdateDTO, UserDTO, UserListDTO,
    AddressCreateDTO, AddressUpdateDTO, AddressDTO,
)
from src.core.enums import UserRole
from src.core.services.user_service import UserService


class CreateUser:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, dto: UserCreateDTO) -> UserDTO:
        return await self.service.create_user(dto)


class GetUser:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> UserDTO:
        return await self.service.get_user(user_id)


class GetUserByTelegramId:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, telegram_id: int) -> UserDTO:
        return await self.service.get_user_by_telegram_id(telegram_id)


class UpdateUser:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int, dto: UserUpdateDTO) -> UserDTO:
        return await self.service.update_user(user_id, dto)


class DeleteUser:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> bool:
        return await self.service.delete_user(user_id)


class ListUsers:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, *, offset: int = 0, limit: int = 100) -> list[UserListDTO]:
        return await self.service.list_users(offset=offset, limit=limit)


class ListUsersByRole:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, role: UserRole, *, offset: int = 0, limit: int = 100) -> list[UserListDTO]:
        return await self.service.list_by_role(role, offset=offset, limit=limit)


class DeactivateUser:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> bool:
        return await self.service.deactivate_user(user_id)


class AdjustBalance:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int, amount: Decimal) -> Decimal:
        return await self.service.adjust_balance(user_id, amount)


class GetByReferralCode:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, code: str) -> UserDTO:
        return await self.service.get_by_referral_code(code)


# ── Address Use Cases ──

class CreateAddress:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int, dto: AddressCreateDTO) -> AddressDTO:
        return await self.service.create_address(user_id, dto)


class GetAddresses:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int) -> list[AddressDTO]:
        return await self.service.get_addresses(user_id)


class UpdateAddress:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, user_id: int, address_id: int, dto: AddressUpdateDTO) -> AddressDTO:
        return await self.service.update_address(user_id, address_id, dto)


class DeleteAddress:
    def __init__(self, service: UserService):
        self.service = service

    async def execute(self, address_id: int) -> bool:
        return await self.service.delete_address(address_id)
