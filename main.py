from fastapi import FastAPI,Depends,HTTPException,status,WebSocket,WebSocketDisconnect,BackgroundTasks,UploadFile, File
from database import get_db,Base,engine
from sqlalchemy.orm import Session
from sqlalchemy import select,or_,func
from models.users import User
from models.posts import Post
from models.comments import Comment
from models.follows import Follows
from models.likes import Like
from schemas.users import UserCreate,UserResponse,Token,UserUpdate
from schemas.posts import PostCreate,PostResponse,PostUpdate,PostOut
from schemas.comments import CommentCreate,CommentResponse
from core import security,auth,socket_manager
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import shutil
import os

app=FastAPI()
manager=socket_manager.ConnectionManager()

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
    # to allow login either via email or username
    result=db.execute(select(User).where(or_(User.username==form_data.username,User.email==form_data.username)))
    
    existing_user=result.scalars().first()
    
    if not existing_user or not security.verify_password(form_data.password,existing_user.hashed_password):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    # Storing user identity in sub claim
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
def get_me(current_user: User = Depends(auth.get_current_user)):
    return current_user
  
  
@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate,db: Session = Depends(get_db),current_user: User = Depends(auth.get_current_user)):
    
    new_post=Post(**post.model_dump(),owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get('/posts',response_model=list[PostOut])
def get_posts(search:Optional[str]="",db:Session=Depends(get_db),limit:int=10,skip:int=0):
    result=db.execute(select(Post,func.count(Like.post_id).label("likes_count")).outerjoin(Like,Post.id==Like.post_id).filter(or_(Post.title.contains(search),Post.content.contains(search))).group_by(Post.id).limit(limit).offset(skip))
    posts=result.all()
    return [
        {
            "post": post,
            "likes_count": likes_count
        }
        for post, likes_count in posts
    ]

@app.patch('/posts/{post_id}',response_model=PostResponse)
def update_post(post_update:PostUpdate,post_id:int,db:Session=Depends(get_db),current_user:User=Depends(auth.get_current_user)):
    result=db.execute(
        select(Post).where(Post.id==post_id)
    )
    post=result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    update_data=post_update.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(post,field,value)
    db.commit()
    db.refresh(post)
    return post

@app.delete('/posts/{post_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int,db:Session=Depends(get_db),current_user:User=Depends(auth.get_current_user)):
    result=db.execute(
        select(Post).where(Post.id==post_id)
    )
    post=result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    db.delete(post)
    db.commit()

@app.post('/posts/{post_id}/comments',response_model=CommentResponse,status_code=status.HTTP_201_CREATED)
def create_comment(post_id:int,comment:CommentCreate,db:Session=Depends(get_db),current_user:User=Depends(auth.get_current_user)):
    result=db.execute(
        select(Post).where(Post.id==post_id)
    )
    post=result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    
    new_comment=Comment(**comment.model_dump(),owner_id=current_user.id,post_id=post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.post("/users/{target_user_id}/follow", status_code=status.HTTP_200_OK)
def follow_toggle(target_user_id:int,db:Session=Depends(get_db),current_user:User=Depends(auth.get_current_user)):
    
    if current_user.id==target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Request")
    
    result=db.execute(
        select(User).where(User.id==target_user_id)
    )
    user=result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    
    result=db.execute(
        select(Follows).where(Follows.follower_id==current_user.id,Follows.followed_id==target_user_id)
    )
    
    found_follow=result.scalars().first()
    
    if found_follow:
        db.delete(found_follow)
        db.commit()
        return {"message": "Successfully unfollowed user"}
    
    new_follow = Follows(follower_id=current_user.id, followed_id=target_user_id)
    db.add(new_follow)
    db.commit()
    return {"message": "Successfully followed user"}
    
    
@app.post("/posts/{post_id}/like", status_code=status.HTTP_200_OK)
def like_toggle(post_id:int,background_tasks: BackgroundTasks,db:Session=Depends(get_db),current_user:User=Depends(auth.get_current_user),):
    result=db.execute(
        select(Post).where(Post.id==post_id)
    )
    post=result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    
    result=db.execute(
        select(Like).where(Like.post_id==post_id,Like.user_id==current_user.id)
    )
    
    found_like=result.scalars().first()
    
    if found_like:
        db.delete(found_like)
        db.commit()
        return {"message":"Post unliked"}
    
    new_like = Like(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    db.commit()
    notification_msg = f'{{"type": "like", "post_id": {post_id}, "message": "User {current_user.username} liked your post!"}}'
    
    background_tasks.add_task(
        manager.send_personal_message, 
        notification_msg, 
        post.owner_id  # <--- We target the owner of the post!
    )
    return {"message": "Post liked"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    
    await manager.connect(
        websocket,
        user_id
    )
    try:

        while True:

            data = await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(user_id)


@app.patch("/users/me", response_model=UserResponse)
def update_user(user_update: UserUpdate,db:Session=Depends(get_db), current_user:User=Depends(auth.get_current_user)):
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
     setattr(current_user, field, value)
        
    # 3. Save and return
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/users/me/avatar", response_model=UserResponse)
def upload_profile(file: UploadFile = File(...),db:Session=Depends(get_db), current_user:User=Depends(auth.get_current_user)):
    os.makedirs("static/images", exist_ok=True)
    file_location = f"static/images/user_{current_user.id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    current_user.profile_image_url = f"/{file_location}"
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/posts/{post_id}/image", response_model=PostResponse)
def upload_image(post_id: int, file: UploadFile = File(...), db: Session=Depends(get_db), current_user: User=Depends(auth.get_current_user)):
    result=db.execute(
        select(Post).where(Post.id==post_id)
    )
    post=result.scalars().first()
    
    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    
    os.makedirs("static/post_images", exist_ok=True)
    file_location = f"static/post_images/post_{post.id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    post.image_url = f"/{file_location}"
    db.commit()
    db.refresh(post)
    return post