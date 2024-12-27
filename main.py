 
from fastapi import Depends ,FastAPI, HTTPException
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base  
from sqlalchemy.orm import Session,sessionmaker
from passlib.context import CryptContext
from fastapi import HTTPException
from starlette import status

DATABASE_URL ="sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__="users"

    id = Column (Integer, primary_key=True,index=True)
    username = Column (String, unique=True,index=True)
    hashed_password =Column(String)

class Post(Base):
    __tablename__="posts"

    id = Column (Integer, primary_key=True,index=True)
    title = Column(String, index=True)
    content=Column(String)
    owner_id=Column(Integer,ForeignKey("users.id")) 

#create tables
Base.metadata.create_all(bind=engine)


#database session
def get_db() :
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

app=FastAPI()

pwd_context=CryptContext(schemes=["bcrypt"])
SessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.post("/register", response_model=dict)
def register(username:str, password:str, db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.username==username).first()
    if(existing_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = pwd_context.hash(password)
    new_user =User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return{"success":True, "message":"User registered successfully"}

@app.post("/login", response_model=dict)
def login(username:str, password:str, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return{"success":True, "message":"User Logged In Successfully", "user_id":user.id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ceredentials",
        )
    
        
     

@app.post("/add-post/{user.id}", response_model=dict)  
def add_post(title:str, content:str, user_id:int, db:Session=Depends(get_db)) :
    new_Post =Post(title=title, content=content, owner_id=user_id)
    db.add(new_Post)
    db.commit()
    db.refresh(new_Post)
    return{"success":True, "message":"Post added successfully"}
 

@app.put("/update.post/{post.id},respomse_model=dict") 
def update_post(post_id:int , title:str, content:str,db:Session=Depends(get_db)) :
    post =db.query(Post).filters(Post.id==post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found",
        )
    post.title =title
    post.content =content
    db.commit()
    db.refresh(post)
    return{"success":True,"message":"Post updated Successfully"}

@app.get("getposts/{user_id}",response_model=list[dict])
def get_user_posts(user_id:int ,db:Session=Depends(get_db)):
    user_post = db.filter(Post).filter(Post.owner_id==user_id)
    return[
        {
            "id":post.id,
            "title":post.title, 
            "content":post.content,
        }
        for post in user_post
    ]

        



    