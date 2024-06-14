from pydantic import BaseModel

class CreateAdmin(BaseModel):
    username: str
    password: str