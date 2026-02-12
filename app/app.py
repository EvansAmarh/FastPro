from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, UserCreate, UserRead, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models import UploadFileRequestOptions
from app.users import auth_backend, current_active_user, fastapi_users

import shutil
import os
import uuid
import tempfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), caption: str = Form(""), user: User = Depends(current_active_user), session: AsyncSession = Depends(get_async_session)):
    temp_file_path = None
    try: 
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            
            upload_result = imagekit.upload_file(
                 file=open(temp_file_path, "rb"),
                file_name = file.filename,
                options = UploadFileResquestOptions(
                    use_unique_file_name=True,
                    tags = ["backend upload"]
                )
            )
            
            if upload_result.response_metadata.http_status_code == 200:
            
                post = Post(
                    user_id=user.id,
                    caption=caption, 
                    url=upload_result.url, 
                    file_type="video" if file.content_type.startswith("video/") else "image", 
                    file_name=upload_result.name)
                
                session.add(post)
                await session.commit()
                await session.refresh(post)
                return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()
        
        
@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    results = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in results.all()]
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}
    
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post(user.id)),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )
        return {"post": posts_data}
    
    
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't permission to delete this post")
        
        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# text_posts = {
#     1: {"title": "Book lib", "content": "Best Western Plus"},
#     2: {"title": "Tech Trends", "content": "Exploring the future of AI innovations"},
#     3: {"title": "Health Hub", "content": "Your daily dose of wellness tips"},
#     4: {"title": "Food Fiesta", "content": "Discover recipes from around the world"},
#     5: {"title": "Travel Tales", "content": "Adventures across continents"},
#     6: {"title": "Movie Mania", "content": "Top-rated films and reviews"},
#     7: {"title": "Code Craft", "content": "Mastering Python and web development"},
#     8: {"title": "Finance Focus", "content": "Smart investment strategies"},
#     9: {"title": "Eco Earth", "content": "Sustainable living and green energy"},
#     10: {"title": "Gadget Geek", "content": "Latest reviews on tech gadgets"},
# }

# @app.get("/post")
# def post(limit: int=None):
#     if limit:
#         return list(text_posts.values())[:limit]
#     return text_posts

# @app.get("/post/{id}")
# def get_post(id: int)->CreatePost:
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post Not found")
#     return text_posts.get(id)

# @app.post("/posts")
# def create_post(post: CreatePost)->CreatePost:
#     new_post = {"title": post.title, "content": post.content}
#     text_posts[max(text_posts.key()) + 1] = new_post
#     return new_post