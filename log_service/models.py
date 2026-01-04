from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
