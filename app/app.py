from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), caption: str = Form(""), session: AsyncSession = Depends(get_async_session)):
    pass
    
    


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