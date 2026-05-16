from fastapi import FastAPI,Depends,HTTPException,status
from database import get_db,Base,engine
from sqlalchemy.orm import Session
from sqlalchemy import select,or_
from models.users import User
from schemas.users import UserCreate,UserResponse,Token
from core import security,auth
from fastapi.security import OAuth2PasswordRequestForm

app=FastAPI()

Base.metadata.create_all(bind=engine)

@app.post('/register',response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register_user(user:UserCreate,db:Session=Depends(get_db)):
    
    result=db.execute(select(User).where(or_(User.username==user.username,User.email==user.email)))
    existing_user=result.scalars().first()
    if existing_user:
        if existing_user.username==user.username:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists")
        if existing_user.email==user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="email already registered")
            
    
    hashed_pw=security.get_password_hash(user.password)
    
    new_user=User(
        username=user.username,
        hashed_password=hashed_pw,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    
@app.post('/login',response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    
    result=db.execute(select(User).where(or_(User.username==form_data.username,User.email==form_data.username)))
    
    existing_user=result.scalars().first()
    
    if not existing_user or not security.verify_password(form_data.password,existing_user.hashed_password):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
  
    access_token = auth.create_access_token(
        data={
            "sub": str(existing_user.id)
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user
  
  
    