from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils import get_current_user, hash_pwd, validate_password, verify_pwd
from ..schema import CreateUser, PasswordUpdate
router = APIRouter(prefix="/user",tags=['User'])

@router.post("",status_code=status.HTTP_201_CREATED)
def create_user(user : CreateUser,db:Session = Depends(get_db)):
    email_exists = db.query(User).filter(User.email == user.email)
    if email_exists.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Email: '{user.email}' already exists")
    username_exists = db.query(User).filter(User.username == user.username)
    if username_exists.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Username: '{user.username}' already exists.")
    
    is_valid,message = validate_password(user.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
    
    user_data = User(**user.dict())
    hashed_password = hash_pwd(user.password)
    user_data.password = hashed_password
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {"message":"Created","user":user_data}


@router.patch("",status_code=status.HTTP_201_CREATED)
def update_password(update_body:PasswordUpdate,db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == update_body.username)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Username: {update_body.username} does not exists")
    
    if not verify_pwd(update_body.old_password,user.first().password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Passwod does not match")

    is_valid,message = validate_password(update_body.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)

    hashed = hash_pwd(update_body.  new_password)
    user.update({"password":hashed},synchronize_session=False)
    db.commit()
    return {"message":"updated"}