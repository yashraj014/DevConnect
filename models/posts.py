from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import datetime,UTC
from __future__ import annotations

class Post(Base):
    __tablename__="posts"
    
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    title:Mapped[str]=mapped_column(String,nullable=False)
    content:Mapped[str]=mapped_column(String,nullable=False)
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    owner_id:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    owner:Mapped["User"]=relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")
    likes: Mapped[list["Like"]] = relationship(back_populates="post")