from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, Token
from passlib.context import CryptContext
from jose import jwt
import datetime

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"])

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: UserCreate):
    db: Session = next(get_db())
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "user exists")

    hashed = pwd_context.hash(user.password)
    new_user = User(username=user.username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    return {"status": "ok"}

@app.post("/login", response_model=Token)
def login(user: UserCreate):
    db: Session = next(get_db())
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(401, "bad credentials")

    payload = {
        "sub": str(db_user.id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}
