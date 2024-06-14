import hashlib
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from router.model import User

async def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def authenticate(credentials: HTTPBasicCredentials, session: AsyncSession):
    hashed_password = await hash_password(credentials.password)
    query = select(User).where(
        User.username == credentials.username,
        User.password == hashed_password
    )
    result = await session.execute(query)
    return result.scalars().first()