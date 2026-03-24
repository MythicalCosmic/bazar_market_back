from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ── User (admin view) ──

class UserCreateDTO(BaseModel):
    telegram_id: int | None = None
    username: str | None = Field(None, max_length=100)
    first_name: str = Field(..., max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    role: str = Field("client", max_length=20)
    language: str = Field("uz", max_length=5)


class AdminCreateDTO(BaseModel):
    username: str = Field(..., max_length=100)
    first_name: str = Field(..., max_length=100)
    last_name: str | None = Field(None, max_length=100)
    password: str = Field(..., min_length=6)
    permissions: list[str] = []


class UserUpdateDTO(BaseModel):
    username: str | None = Field(None, max_length=100)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    language: str | None = Field(None, max_length=5)


class UserDTO(BaseModel):
    id: int
    telegram_id: int | None
    username: str | None
    first_name: str
    last_name: str | None
    phone: str | None
    referral_code: str | None
    balance: Decimal
    role: str
    language: str
    permissions: list[str] = []
    is_verified: bool
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime
    addresses: list["AddressDTO"] = []

    model_config = {"from_attributes": True}


class UserListDTO(BaseModel):
    id: int
    telegram_id: int | None
    username: str | None
    first_name: str
    last_name: str | None
    phone: str | None
    role: str
    permissions: list[str] = []
    is_verified: bool
    is_active: bool
    last_seen_at: datetime | None

    model_config = {"from_attributes": True}


# ── Customer (own view) ──

class CustomerProfileDTO(BaseModel):
    id: int
    telegram_id: int | None
    username: str | None
    first_name: str
    last_name: str | None
    phone: str | None
    balance: Decimal
    language: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerProfileUpdateDTO(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    language: str | None = Field(None, max_length=5)


# ── Address ──

class AddressCreateDTO(BaseModel):
    label: str | None = Field(None, max_length=100)
    latitude: Decimal = Field(..., decimal_places=7)
    longitude: Decimal = Field(..., decimal_places=7)
    address_text: str
    entrance: str | None = Field(None, max_length=20)
    floor: str | None = Field(None, max_length=10)
    apartment: str | None = Field(None, max_length=20)
    comment: str | None = None
    is_default: bool = False


class AddressUpdateDTO(BaseModel):
    label: str | None = Field(None, max_length=100)
    latitude: Decimal | None = Field(None, decimal_places=7)
    longitude: Decimal | None = Field(None, decimal_places=7)
    address_text: str | None = None
    entrance: str | None = Field(None, max_length=20)
    floor: str | None = Field(None, max_length=10)
    apartment: str | None = Field(None, max_length=20)
    comment: str | None = None
    is_default: bool | None = None


class AddressDTO(BaseModel):
    id: int
    user_id: int
    label: str | None
    latitude: Decimal
    longitude: Decimal
    address_text: str
    entrance: str | None
    floor: str | None
    apartment: str | None
    comment: str | None
    is_default: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
