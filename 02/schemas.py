from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author: UserPublic


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=20)
    email: EmailStr


class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)
    password_hash: str = Field(min_length=8)

    # image_file:str|  None
    # image_path:str | None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    image_file: str | None
    image_path: str | None


class UserPrivate(UserPublic):
    email: EmailStr


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = Field(default=None, min_length=1)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = Field(default=None)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)
