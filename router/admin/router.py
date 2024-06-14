from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import get_async_session
from sqlalchemy import select, insert

from router.admin.shemas import CreateAdmin
from router.admin.function import hash_password, authenticate
from router.model import User

security = HTTPBasic()

router = APIRouter(prefix="/api/v1/routes", tags=["admin"])

@router.post("/register/admin")
async def register_admin(admin_create: CreateAdmin, session: AsyncSession = Depends(get_async_session)):
    hash_pass = await hash_password(admin_create.password)
    admin_create.password = hash_pass
    stmt = insert(User).values(admin_create.dict())
    await session.execute(stmt)
    await session.commit()
    return {"detail": "status success"}

@router.post("/login")
async def login_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)):
    user = await authenticate(credentials, session)
    if not user:
        return {"message": "User not found"}
    return {"message": "Successful login"}