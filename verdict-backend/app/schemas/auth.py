from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    firmId: str
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    success: bool
    data: dict
