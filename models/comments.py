from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import datetime,UTC

class Comment(Base):
    __tablename__="comments"
    
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    content:Mapped[str]=mapped_column(String,nullable=False)
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    owner_id:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    post_id:Mapped[int]=mapped_column(Integer,ForeignKey("posts.id"),nullable=False)
    owner:Mapped["User"]=relationship(back_populates="comments")
    post:Mapped["Post"]=relationship(back_populates="comments")