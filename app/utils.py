from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext    
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
from app.schema import TokenData 
from .config import settings
import re

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_pwd(password:str):
    return pwd_context.hash(password)

def verify_pwd(plain_pwd,hashed):
    return pwd_context.verify(plain_pwd,hashed)

def create_access_token(data:dict):
    encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp":expire})

    encoded_jwt = jwt.encode(encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_error):
    try:
        payload = jwt.decode(token,key=SECRET_KEY,algorithms=ALGORITHM)
        user_id : int = payload['user_id']
        if user_id is None:
            raise credentials_error
        token_data = TokenData(user_id=user_id)
    except PyJWTError:
        raise credentials_error
    
    return token_data
    
def get_current_user(token:str = Depends(oauth2_scheme),db : Session = Depends(get_db)):
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Can not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    user_data = verify_access_token(token,credentials_error)
    user = db.query(User).filter(User.id == user_data.user_id).first()
    return user


def validate_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 64:
        return False, "Password cannot exceed 64 characters"

    if " " in password:
        return False, "Password cannot contain spaces"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]`~;']", password):
        return False, "Password must contain at least one special character"

    return True, "Valid password"


