from schemas import PostResponse,PostCreate,UserCreate,UserResponse,PostUpdate
import models
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Request, status,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Base,engine,get_db
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media",StaticFiles(directory="media"),name="media")
templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request,db:Annotated[Session,Depends(get_db)]):
    posts = db.execute(select(models.Post)).scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
        },
    )

@app.delete("/api/posts/{post_id}")
def delete_post(post_id:int,db:Annotated[Session,Depends(get_db)]):
    post = db.execute(select(models.Post).where(models.Post.id == post_id)).scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post is not Found!")
    db.delete(post)
    db.commit()
    return "Deleted Successfully!"

@app.delete("/api/users/{user_id}")
def delete_user(user_id:int,db:Annotated[Session,Depends(get_db)]):
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user is not Found!")
    db.delete(user)
    db.commit()
    return "Deleted Successfully!"

@app.put("/api/posts/{post_id}",response_model=PostResponse)
def update_put_post(post_data:PostCreate,post_id:int,db:Annotated[Session,Depends(get_db)]):
     post = db.execute(select(models.Post).where(models.Post.id == post_id)).scalars().first()
     if not post:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post is not Found!")
     if post.user_id !=post_data.user_id:
        user = db.execute(select(models.User).where(models.User.id == post.user_id)).scalars().first()
        if not user:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user is not Found!")
     post.title = post_data.title
     post.content = post_data.content
     post.user_id = post_data.user_id
     
     db.commit()
     db.refresh(post)
     return post
     
@app.put("/api/user/{user_id}",response_model=UserResponse)
def put_update_user(user_id:int,db:Annotated[Session,Depends(get_db)]):
    pass
     

@app.get("/profile", include_in_schema=False, name="profile")
def profiles(request: Request):
    return templates.TemplateResponse(request, "error.html")

@app.patch("/api/")

@app.post("/api/users",response_model=UserResponse)
def create_user(user:UserCreate,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))
    username_exist = result.scalars().first()
    if username_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username already exist!")
    result = db.execute(select(models.User).where(models.User.email == user.email))
    email_exist = result.scalars().first()
    if email_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="email already exist!")
    
    new_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/posts",response_model=PostResponse)
def create_post(post:PostCreate,db:Annotated[Session,Depends(get_db)]):
    user = db.execute(select(models.User).where(models.User.id == post.user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not Found!")
        
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post
    
@app.get("/api/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not found!")
    return user
    
    
@app.get("/post/{post_id}", include_in_schema=False)
def post_page(req: Request, post_id: int,db:Annotated[Session,Depends(get_db)]):
    post = db.execute(select(models.Post).where(models.Post.id == post_id)).scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    title = post.title[:50]
    return templates.TemplateResponse(req,"post.html",{"post":post,"title":title})
    
@app.get("/user/{user_id}/posts",name="user_post_page",include_in_schema=False)
def user_post_page(req:Request,user_id:int,db:Annotated[Session,Depends(get_db)]):
    user_post = db.execute(select(models.Post).where(models.Post.user_id == user_id)).scalars().all()
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not found!")
    return templates.TemplateResponse(req,"user_posts.html",{"posts":user_post,"user":user,"title": f"{user.username}'s Posts"})
        


@app.get("/api/posts",response_model=list[PostResponse])
def get_posts(db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post)).scalars().all()
    return result

@app.get("/api/user/{user_id}/posts",response_model=list[PostResponse])
def user_post(user_id:int,db:Annotated[Session,Depends(get_db)]):
    user_post = db.execute(select(models.Post).where(models.Post.user_id == user_id)).scalars().all()
    if not user_post:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User is not found!")
    return user_post
    

@app.get("/api/post/{post_id}",response_model=PostResponse)
def get_post(post_id: int,db:Annotated[Session,Depends(get_db)]):
    post = db.execute(select(models.Post).where(models.Post.id == post_id)).scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post is not Found!")
    return post


@app.exception_handler(StarletteHTTPException)
def handle_starlette_exception(req:Request,exc:StarletteHTTPException):
    if req.url.path.startswith("/api"):
      return JSONResponse(status_code=exc.status_code,content={"msg":exc.detail})
    return templates.TemplateResponse(req,"error.html",{
        "status_code":exc.status_code,
        "error_title":exc.detail,
    },status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
def handle_exception(req:Request,exc:RequestValidationError):
    if req.url.path.startswith("/api"):
      return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,content=exc.errors())
  
    return templates.TemplateResponse(req,"error.html",{
        "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
        "error_title":exc.errors()[0]["msg"],
        "error_msg":f"{exc.errors()[0]["type"]} -- value got -- {exc.errors()[0]["input"]}"
    })
