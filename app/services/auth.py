from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()



def hash_password(password: str):
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    password = password[:72]
    return pwd_context.verify(password, hashed)


def create_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=2)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token=Depends(security)):

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]

    except:
        raise HTTPException(status_code=401, detail="Invalid token")