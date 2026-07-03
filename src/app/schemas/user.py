from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    """Used when someone sends a POST /register request"""
    email: EmailStr        # validates it's a real email format automatically
    password: str          # plain text — we hash it in the service layer

class UserLogin(BaseModel):
    """Used when someone sends a POST /login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """What we send back — notice: no password field"""
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        # Django comparison: similar to serializers with source model
        # This lets Pydantic read from SQLAlchemy model objects directly
        # Without this, it can't convert a User model instance to JSON

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"