from fastapi import status, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..schema import Token
from ..models import User
from ..utils import create_access_token, verify_pwd


router = APIRouter()

@router.post("/login",response_model=Token)
def login(user_credentials : OAuth2PasswordRequestForm = Depends(),db : Session = Depends(get_db)):
    user = db.query(User).filter(or_(User.email == user_credentials.username,User.username == user_credentials.username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")
    if not verify_pwd(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentils")
    # create token
    token = create_access_token(data={"user_id": user.id})
    return {"access_token":token,"token_type":"Bearer"}
