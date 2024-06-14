from pydantic import BaseModel
from typing import Optional

class CreateClients(BaseModel):
    name: str
    number: str
    city: str

class ProductUpdate(BaseModel):
    weight: Optional[float]
    amount: Optional[int]