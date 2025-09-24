from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login payload with validated email and password."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    role: str
    token_type: str = "bearer"
