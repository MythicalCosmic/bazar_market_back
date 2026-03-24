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