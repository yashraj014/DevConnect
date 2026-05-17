from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import datetime,UTC


class Follows(Base):
    __tablename__='follows'
    follower_id:Mapped[int]=mapped_column(ForeignKey("users.id"),primary_key=True)
    followed_id:Mapped[int]=mapped_column(ForeignKey("users.id"),primary_key=True)
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    # The user who is doing the following
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    
    # The user who is being followed
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id], back_populates="followers")