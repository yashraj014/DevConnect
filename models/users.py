from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from database import Base
from datetime import datetime,UTC

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