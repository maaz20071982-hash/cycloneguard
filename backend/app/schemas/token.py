from pydantic import BaseModel
from app.schemas.user import UserResponse


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int


class LoginSuccessData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
