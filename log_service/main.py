from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Log
from schemas import LogCreate, LogOut

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/log")
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    new_log = Log(**log.model_dump())
    db.add(new_log)
    db.commit()
    return {"status": "logged"}

@app.get("/logs", response_model=list[LogOut])
def get_logs(db: Session = Depends(get_db)):
    return db.query(Log).order_by(Log.created_at.desc()).all()
