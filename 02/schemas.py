from __future__ import annotations
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PostBase(BaseModel):
    title:str = Field(min_length=1,max_length=50)
    content:str=Field(min_length=1)


class PostCreate(PostBase):
    model_config = ConfigDict(from_attributes=True)
    user_id:int 



class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id:int
    author:UserResponse
    
class UserBase(BaseModel):
    username:str = Field(min_length=1,max_length=20)
    email:EmailStr


class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    # image_file:str|  None
    # image_path:str | None

    
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id:int
    image_file:str|  None
    image_path:str | None

class PostUpdate(BaseModel):
    title:str | None = Field(default=None,min_length=1,max_length=50)
    content:str | None = Field(default=None,min_length=1)

class UserUpdate(BaseModel): 
    username:str | None = Field(default=None,min_length=1,max_length=20)
    email:EmailStr
    image_file:str|  None =  Field(default=None, min_length=1, max_length=200)