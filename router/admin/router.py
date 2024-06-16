from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBasic
from database import get_async_session
from sqlalchemy import insert
from fastapi.security.api_key import APIKey 

from router.shemas import CreateAdmin
from functions import hash_password
from router.model import User
from router.api_conf import get_api_key

security = HTTPBasic()

router = APIRouter(prefix="/api/v1/routes", tags=["admin"])

@router.post("/register/admin")
async def register_admin(admin_create: CreateAdmin, 
                        session: AsyncSession = Depends(get_async_session), 
                        api_key: APIKey = Depends(get_api_key)
                        ):
    hash_pass = await hash_password(admin_create.password)
    admin_create.password = hash_pass
    stmt = insert(User).values(admin_create.dict())
    await session.execute(stmt)
    await session.commit()
    return {"detail": "status success"}

