from __future__ import annotations
from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import datetime,UTC
from models.posts import Post



class User(Base):
    __tablename__="users"
    
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    email:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    username:Mapped[str]=mapped_column(String(50),unique=True,index=True,nullable=False)
    hashed_password:Mapped[str]=mapped_column(String,nullable=False)
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    bio: Mapped[str] = mapped_column(String, nullable=True)
    github_link: Mapped[str] = mapped_column(String, nullable=True)
    profile_image_url: Mapped[str] = mapped_column(String, nullable=True)
    posts:Mapped[list["Post"]]=relationship(back_populates="owner")
    comments: Mapped[list["Comment"]] = relationship(back_populates="owner")
    # Who is this user following?
    following: Mapped[list["Follows"]] = relationship("Follows", foreign_keys="[Follows.follower_id]", back_populates="follower")
    
    # Who follows this user?
    followers: Mapped[list["Follows"]] = relationship("Follows", foreign_keys="[Follows.followed_id]", back_populates="followed")
    likes: Mapped[list["Like"]] = relationship(back_populates="user")

