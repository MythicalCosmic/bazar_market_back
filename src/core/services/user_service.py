import secrets
from decimal import Decimal

from src.core.dto.user import (
    UserCreateDTO, UserUpdateDTO, UserDTO, UserListDTO,
    AddressCreateDTO, AddressUpdateDTO, AddressDTO,
)
from src.core.enums import UserRole
from src.core.exceptions import NotFoundException, AlreadyExistsException
from src.core.interfaces.user_interface import IUserRepository, IAddressRepository


class UserService:
    def __init__(self, user_repo: IUserRepository, address_repo: IAddressRepository):
        self.user_repo = user_repo
        self.address_repo = address_repo


    async def create_user(self, dto: UserCreateDTO) -> UserDTO:
        if dto.telegram_id and await self.user_repo.get_by_telegram_id(dto.telegram_id):
            raise AlreadyExistsException("User", "telegram_id", str(dto.telegram_id))
        if dto.phone and await self.user_repo.get_by_phone(dto.phone):
            raise AlreadyExistsException("User", "phone", dto.phone)
        if dto.username and await self.user_repo.get_by_username(dto.username):
            raise AlreadyExistsException("User", "username", dto.username)

        referral_code = secrets.token_urlsafe(8)
        user = await self.user_repo.create(
            **dto.model_dump(exclude_unset=True),
            referral_code=referral_code,
        )
        return UserDTO.model_validate(user)

    async def get_user(self, user_id: int) -> UserDTO:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserDTO.model_validate(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserDTO:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise NotFoundException("User", telegram_id)
        return UserDTO.model_validate(user)

    async def update_user(self, user_id: int, dto: UserUpdateDTO) -> UserDTO:
        data = dto.model_dump(exclude_unset=True)
        if not data:
            return await self.get_user(user_id)

        if "phone" in data and data["phone"]:
            existing = await self.user_repo.get_by_phone(data["phone"])
            if existing and existing.id != user_id:
                raise AlreadyExistsException("User", "phone", data["phone"])

        if "username" in data and data["username"]:
            existing = await self.user_repo.get_by_username(data["username"])
            if existing and existing.id != user_id:
                raise AlreadyExistsException("User", "username", data["username"])

        user = await self.user_repo.update_by_id(user_id, **data)
        if not user:
            raise NotFoundException("User", user_id)
        return UserDTO.model_validate(user)

    async def delete_user(self, user_id: int) -> bool:
        deleted = await self.user_repo.soft_delete(user_id)
        if not deleted:
            raise NotFoundException("User", user_id)
        return True


    async def list_users(self, *, offset: int = 0, limit: int = 100) -> list[UserListDTO]:
        users = await self.user_repo.get_all(offset=offset, limit=limit)
        return [UserListDTO.model_validate(u) for u in users]

    async def list_by_role(self, role: UserRole, *, offset: int = 0, limit: int = 100) -> list[UserListDTO]:
        users = await self.user_repo.get_by_role(role, offset=offset, limit=limit)
        return [UserListDTO.model_validate(u) for u in users]

    async def list_active(self, *, offset: int = 0, limit: int = 100) -> list[UserListDTO]:
        users = await self.user_repo.get_active(offset=offset, limit=limit)
        return [UserListDTO.model_validate(u) for u in users]

    async def count_users(self) -> int:
        return await self.user_repo.count()


    async def deactivate_user(self, user_id: int) -> bool:
        deactivated = await self.user_repo.deactivate(user_id)
        if not deactivated:
            raise NotFoundException("User", user_id)
        return True

    async def touch_last_seen(self, user_id: int) -> None:
        await self.user_repo.touch_last_seen(user_id)

    async def adjust_balance(self, user_id: int, amount: Decimal) -> Decimal:
        new_balance = await self.user_repo.adjust_balance(user_id, amount)
        if new_balance is None:
            raise NotFoundException("User", user_id)
        return new_balance

    async def get_by_referral_code(self, code: str) -> UserDTO:
        user = await self.user_repo.get_by_referral_code(code)
        if not user:
            raise NotFoundException("User", code)
        return UserDTO.model_validate(user)


    async def create_address(self, user_id: int, dto: AddressCreateDTO) -> AddressDTO:
        await self._ensure_user_exists(user_id)
        if dto.is_default:
            await self.address_repo.set_default(user_id, -1)  # unset all
        address = await self.address_repo.create(user_id=user_id, **dto.model_dump())
        if dto.is_default:
            await self.address_repo.set_default(user_id, address.id)
        return AddressDTO.model_validate(address)

    async def get_addresses(self, user_id: int) -> list[AddressDTO]:
        addresses = await self.address_repo.get_by_user(user_id)
        return [AddressDTO.model_validate(a) for a in addresses]

    async def update_address(self, user_id: int, address_id: int, dto: AddressUpdateDTO) -> AddressDTO:
        data = dto.model_dump(exclude_unset=True)
        is_default = data.pop("is_default", None)

        if data:
            address = await self.address_repo.update_by_id(address_id, **data)
            if not address:
                raise NotFoundException("Address", address_id)

        if is_default is True:
            await self.address_repo.set_default(user_id, address_id)

        address = await self.address_repo.get_by_id(address_id)
        return AddressDTO.model_validate(address)

    async def delete_address(self, address_id: int) -> bool:
        deactivated = await self.address_repo.deactivate(address_id)
        if not deactivated:
            raise NotFoundException("Address", address_id)
        return True

    async def get_default_address(self, user_id: int) -> AddressDTO | None:
        address = await self.address_repo.get_default(user_id)
        return AddressDTO.model_validate(address) if address else None


    async def _ensure_user_exists(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
