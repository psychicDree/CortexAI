from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class SessionCreate(BaseModel):
    mood: Optional[str] = None
    duration_seconds: int = 0


class SessionOut(BaseModel):
    id: int
    user_id: int
    mood: Optional[str] = None
    started_at: datetime
    duration_seconds: int

    class Config:
        from_attributes = True

