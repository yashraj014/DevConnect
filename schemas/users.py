from pydantic import BaseModel,EmailStr,Field,ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username:str
    email:EmailStr

class UserCreate(UserBase):
    password:str=Field(min_length=5,max_length=50)
    
class UserUpdate(BaseModel):
    bio: str | None = None
    github_link: str | None = None
    
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id:int  
    created_at:datetime
    bio: str | None = None
    github_link: str | None = None
    profile_image_url: str | None = None
    
class Token(BaseModel):
    access_token:str
    token_type:str="bearer"