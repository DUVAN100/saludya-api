from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {"example": {
        "email": "doctor@clinic.com",
        "password": "secret123",
    }}}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"