from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import datetime,UTC

class Like(Base):
    __tablename__="likes"
    
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"),primary_key=True)
    post_id:Mapped[int]=mapped_column(Integer,ForeignKey("posts.id"),primary_key=True)
    user:Mapped["User"]=relationship(back_populates="likes")
    post:Mapped["Post"]=relationship(back_populates="likes")