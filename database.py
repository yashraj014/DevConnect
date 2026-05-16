from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

DATABASE_URL="sqlite:///./dev.db"

class Base(DeclarativeBase):
    pass

engine=create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

def get_db():
   with SessionLocal() as db:
       yield db
    