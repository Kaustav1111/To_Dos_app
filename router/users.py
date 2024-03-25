from fastapi import APIRouter, Depends, Path, HTTPException, status
from models import Users
from database import Sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import decode_jwt_token
from passlib.context import CryptContext
import warnings
warnings.filterwarnings("ignore")

router = APIRouter(prefix="/users",
                   tags=["users"])

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(decode_jwt_token)]
bcrypt_context = CryptContext(schemes=['bcrypt'])



class New_Password_Request(BaseModel):
    new_pass : str = Field(min_length=5)



@router.get("/user_details")
def get_details(user : user_dependency, active_db : db_dependency):
    if user is None:
        raise HTTPException(status_code=401 , detail="Authentication Failed")
    return active_db.query(Users).filter(Users.id == user.get("id")).first()



@router.put("/update_password")
def update_password(user : user_dependency, 
                    active_db : db_dependency, 
                    new_password : New_Password_Request):
    if user is None:
        raise HTTPException(status_code=401 , detail="Authentication Failed")
    
    update_model = active_db.query(Users).filter(Users.id == user.get("id")).first()
    if update_model is None:
        raise HTTPException(status_code=404 , detail="User not found")
    
    update_model.hashed_password = bcrypt_context.hash(new_password.new_pass)
    active_db.add(update_model)
    active_db.commit()



@router.put("/update_phone_number/{phn}")
def update_phone(user : user_dependency,
                 active_db : db_dependency,
                 phn : str = Path(min_length=10)):
    
    if user is None:
        raise HTTPException(status_code=401 , detail="Authentication Failed")
    
    user_model = active_db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phn
    active_db.add(user_model)
    active_db.commit()


