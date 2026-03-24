from pydantic import BaseModel, Field


class AdminLoginDTO(BaseModel):
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshDTO(BaseModel):
    refresh_token: str
