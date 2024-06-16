from pydantic import BaseModel
from typing import Optional
from typing import List

class CreateAdmin(BaseModel):
    username: str
    email: str
    password: str


class CreateClients(BaseModel):
    name: str
    number: str
    city: str

class ProductUpdate(BaseModel):
    weight: Optional[float]
    amount: Optional[int]


class UpdateProductStatusRequest(BaseModel):
    product_ids: List[int]