from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from config import API_KEYS

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")