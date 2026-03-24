from enum import StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    ADMIN = "admin"
    COURIER = "courier"
    MANAGER = "manager"


class Language(StrEnum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


class AdminPermission(StrEnum):
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    USERS_VERIFY = "users.verify"
    USERS_BALANCE = "users.balance"
    ADMINS_MANAGE = "admins.manage"

    @classmethod
    def all(cls) -> list[str]:
        return [p.value for p in cls]
