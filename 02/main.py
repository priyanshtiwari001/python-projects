from contextlib import asynccontextmanager
from typing import Annotated
from auth import hash_password
import models
from databases import Base, engine, get_db
from fastapi import Depends, FastAPI, APIRouter, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import index
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    # shutdown
    await engine.dispose()


# Base.metadata.create_all(bind=engine)


app = FastAPI(lifespan=lifespan)

app.include_router(index.api_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(models.Post).options(selectinload(models.Post.author))
    )
    posts = res.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
        },
    )


@app.get("/profile", include_in_schema=False, name="profile")
async def profiles(request: Request):
    return templates.TemplateResponse(request, "error.html")


# @app.patch("/api/")


@app.get("/post/{post_id}", include_in_schema=False)
async def post_page(
    req: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = res.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    title = post.title[:50]
    return templates.TemplateResponse(req, "post.html", {"post": post, "title": title})


@app.get("/user/{user_id}/posts", name="user_post_page", include_in_schema=False)
async def user_post_page(
    req: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(select(models.Post).where(models.Post.user_id == user_id))
    user_post = res.scalars().all()
    user_res = await db.execute(select(models.User).where(models.User.id == user_id))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not found!"
        )
    return templates.TemplateResponse(
        req,
        "user_posts.html",
        {"posts": user_post, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author))
    )
    posts = result.scalars().all()
    return posts


@app.get("/api/user/{user_id}/posts", response_model=list[PostResponse])
async def user_post(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
    )
    user_post = res.scalars().all()
    if not user_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not found!"
        )
    return user_post


@app.get("/api/post/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = res.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post is not Found!")
    return post


@app.exception_handler(StarletteHTTPException)
async def handle_starlette_exception(req: Request, exc: StarletteHTTPException):
    if req.url.path.startswith("/api"):
        return await http_exception_handler(req, exc)
    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": exc.status_code,
            "error_title": exc.detail,
        },
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def handle_exception(req: Request, exc: RequestValidationError):
    if req.url.path.startswith("/api"):
        return await request_validation_exception_handler(req, exc)

    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "error_title": exc.errors()[0]["msg"],
            "error_msg": f"{exc.errors()[0]["type"]} -- value got -- {exc.errors()[0]["input"]}",
        },
    )
