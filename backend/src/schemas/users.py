from __future__ import annotations
from typing import Optional, List

from pydantic import BaseModel


# === ROLE SCHEMAS ===
class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


class RoleList(BaseModel):
    roles: List[RoleResponse]
    total: int


# === USER SCHEMAS ===
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True


class UserWithRole(UserBase):
    id: int
    role: RoleResponse


class UserList(BaseModel):
    users: List[UserWithRole]
    total: int


# === AUTH SCHEMAS ===
class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    id: int
    username: str
    role: RoleResponse

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional["UserWithRole"] = None


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserWithRole
