
from typing import Annotated

import models
from databases import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import PostCreate, PostResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/posts")

@router.post("",response_model=PostResponse)
async def create_post(post:PostCreate,db:Annotated[AsyncSession,Depends(get_db)]):
    res = await db.execute(select(models.User).where(models.User.id == post.user_id))
    print("res",res)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not Found!")
        
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post,attribute_names=["author"])
    
    return new_post
    

@router.put("/{post_id}",response_model=PostResponse)
async def update_put_post(post_data:PostCreate,post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
     res = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
     post = res.scalars().first()
     if not post:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post is not Found!")
     if post.user_id !=post_data.user_id:
        res = await db.execute(select(models.User).where(models.User.id == post.user_id))
        user = res.scalars().first()
        if not user:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user is not Found!")
     post.title = post_data.title
     post.content = post_data.content
     post.user_id = post_data.user_id
     
     await db.commit()
     await db.refresh(post,attribute_names=["author"])
     return post
 
@router.delete("/{post_id}")
async def delete_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    res = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = res.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post is not Found!")
    await db.delete(post)
    await db.commit()
    return "Deleted Successfully!"



@router.get("/",response_model=list[PostResponse])
async def get_posts(db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    return posts

@router.get("/{post_id}",response_model=PostResponse)
async def get_post(post_id: int,db:Annotated[AsyncSession,Depends(get_db)]):
    res = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = res.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post is not Found!")
    return post

