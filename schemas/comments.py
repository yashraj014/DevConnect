from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime


class CommentBase(BaseModel):
    content:str=Field(min_length=1)
    
class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at:datetime
    owner_id:int
    post_id:int