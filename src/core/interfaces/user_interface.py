from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Sequence

from src.db.models.user import User, Address


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: int) -> User | None: ...

    @abstractmethod
    async def get_all(self, *, offset: int = 0, limit: int = 100) -> Sequence[User]: ...

    @abstractmethod
    async def create(self, **kwargs) -> User: ...

    @abstractmethod
    async def update_by_id(self, id: int, **kwargs) -> User | None: ...

    @abstractmethod
    async def soft_delete(self, id: int) -> bool: ...

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_referral_code(self, code: str) -> User | None: ...

    @abstractmethod
    async def get_by_role(self, role: str, *, offset: int = 0, limit: int = 100) -> Sequence[User]: ...

    @abstractmethod
    async def get_active(self, *, offset: int = 0, limit: int = 100) -> Sequence[User]: ...

    @abstractmethod
    async def touch_last_seen(self, user_id: int) -> None: ...

    @abstractmethod
    async def adjust_balance(self, user_id: int, amount: Decimal) -> Decimal | None: ...

    @abstractmethod
    async def deactivate(self, user_id: int) -> bool: ...

    @abstractmethod
    async def count(self) -> int: ...


class IAddressRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: int) -> Address | None: ...

    @abstractmethod
    async def create(self, **kwargs) -> Address: ...

    @abstractmethod
    async def update_by_id(self, id: int, **kwargs) -> Address | None: ...

    @abstractmethod
    async def get_by_user(self, user_id: int, *, active_only: bool = True) -> Sequence[Address]: ...

    @abstractmethod
    async def get_default(self, user_id: int) -> Address | None: ...

    @abstractmethod
    async def set_default(self, user_id: int, address_id: int) -> None: ...

    @abstractmethod
    async def deactivate(self, address_id: int) -> bool: ...
