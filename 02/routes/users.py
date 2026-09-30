
from typing import Annotated

import models
from databases import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import PostResponse, UserCreate, UserResponse, UserUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users")


@router.get("/{user_id}",response_model=UserResponse)
async def get_user(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not found!")
    return user
  

@router.post("",response_model=UserResponse)
async def create_user(user:UserCreate,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    username_exist = result.scalars().first()
    if username_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username already exist!")
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    email_exist = result.scalars().first()
    if email_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="email already exist!")
    
    new_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.patch("/api/user/{user_id}",response_model=UserResponse)
async def put_update_user(user_data:UserUpdate,user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    res = await db.execute(select(models.User).where(models.User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not Found!")
    if user_data.username is not None and user_data.username != user.username:
        res =  await db.execute(select(models.User).where(models.User.username == user_data.username))
        existing_user = res.scalars().first()
        if existing_user:
             raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username already exist!")
    if user_data.email is not None and user_data.email !=user.email:
        res =  await db.execute(select(models.User).where(models.User.email == user_data.email))
        existing_email = res.scalars().first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="email already exist!")
    
    # if user_data.username is not None:   
    #     user.username = user_data.username
    # if user_data.email is not None:
    #     user.email = user_data.email
    # if user_data.image_file is not None:
    #     user.image_file = user_data.image_file
    user_update = user_data.model_dump(exclude_unset=True) 
    print(type(user_update))
    for key,value in user_update.items():
        setattr(user,key,value)
        
    await db.commit()
    await db.refresh(user)
    return user
        
   

@router.delete("/{user_id}")
async def delete_user(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    res = await db.execute(select(models.User).where(models.User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user is not Found!")
    await db.delete(user)
    await db.commit()
    return "Deleted Successfully!"



@router.get("/{user_id}/posts",response_model=list[PostResponse])
async def user_post(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    user_res = await db.execute(select(models.User).where(models.User.id == user_id))   
    user = user_res.scalars().first()
    if not user:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not found!")
    res = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    user_post = res.scalars().all()
    if not user_post:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post is not found!")
    return user_post
    