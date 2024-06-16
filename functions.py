from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request, Response
from database import get_async_session
import hashlib
from router.model import User
from sqlalchemy import select

from tokenjwt import decode_token, encoded_jwt



async def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def authenticate_user(username, password, session: AsyncSession = Depends(get_async_session)):
    hashed_password = await hash_password(password)
    query = select(User).where(User.username == username, User.password == hashed_password)
    result = await session.execute(query)
    user = result.scalar()
    return user

async def get_user_from_token(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get("token")
    
    if not token:
        return None  

    try:
        token_bytes = token.encode('utf-8')
        token_decode = decode_token(token_bytes)
    except:
        return None 
    
    query = select(User).where(User.username == token_decode["username"])
    result = await session.execute(query)
    user = result.scalar()
    return user

# access generate
async def generate_access_token(user):
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
    }
    return encoded_jwt(user_data)