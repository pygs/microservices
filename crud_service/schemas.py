from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True
