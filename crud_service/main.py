from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Item
from schemas import ItemCreate, ItemOut
from jose import jwt, JWTError
import requests

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"
LOG_SERVICE_URL = "http://localhost:8003/log"

app = FastAPI()
security = HTTPBearer()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid token")

def log_action(user_id: int, action: str):
    try:
        requests.post(LOG_SERVICE_URL, json={
            "user_id": user_id,
            "action": action
        })
    except:
        pass

@app.post("/items", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    new_item = Item(**item.model_dump(), owner_id=user_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    log_action(user_id, f"create item {new_item.id}")
    return new_item

@app.get("/items", response_model=list[ItemOut])
def get_items(db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    return db.query(Item).filter(Item.owner_id == user_id).all()

@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
    if not db_item:
        raise HTTPException(404, "not found")

    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    log_action(user_id, f"update item {item_id}")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
    if not db_item:
        raise HTTPException(404, "not found")

    db.delete(db_item)
    db.commit()
    log_action(user_id, f"delete item {item_id}")
    return {"status": "deleted"}
