import jwt
from pathlib import Path
from config import PrivateKey, PublicKey, algorithm
from datetime import datetime, timedelta

private_key = Path(PrivateKey).read_text()
public_key = Path(PublicKey).read_text()

access_token_exp_min: int = 5
refresh_token_exp_min: int = 4320

def encoded_jwt(
    payload: dict, 
    private_key: str = private_key, 
    algorithm: str = algorithm, 
    exp_min: int = access_token_exp_min
):
    expiry = datetime.utcnow() + timedelta(minutes=exp_min)
    payload['exp'] = expiry
    encoded = jwt.encode(
        payload, 
        private_key, 
        algorithm=algorithm,
    )
    
    return encoded

def encoded_jwt_refresh(
    payload: dict, 
    private_key: str = private_key, 
    algorithm: str = algorithm, 
    exp_min: int = refresh_token_exp_min
):
    expiry = datetime.utcnow() + timedelta(minutes=exp_min)
    payload['exp'] = expiry
    encoded = jwt.encode(
        payload, 
        private_key, 
        algorithm=algorithm,
    )
    return encoded

def decode_token(token: str, public_key: str = public_key, algorithm: str = algorithm):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded
