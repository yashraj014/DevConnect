from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from schemas.comments import CommentResponse

class PostBase(BaseModel):
    title:str=Field(min_length=1,max_length=100)
    content:str=Field(min_length=1)
    
class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title : str | None = Field(default=None,min_length=1,max_length=100)
    content : str | None = Field(default=None,min_length=1)


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at:datetime
    owner_id:int
    image_url: str | None = None
    comments:list[CommentResponse]=[]
    
class PostOut(BaseModel):
    post: PostResponse
    likes_count: int

    model_config = ConfigDict(from_attributes=True)