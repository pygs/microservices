from sqlalchemy import Column, Integer, String, Text
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, nullable=False)
