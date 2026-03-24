from pydantic import BaseModel, Field


class AdminLoginDTO(BaseModel):
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)


class SessionDTO(BaseModel):
    session_token: str
    user_id: int
    role: str
    permissions: list[str] = []
    expires_in: int
