from pydantic import BaseModel
from fastapi_users import schemas
import uuid

class CreatePost(BaseModel):
    title: str
    content: str
    
class ResponsePost(BaseModel):
    title: str
    content: str
    
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass