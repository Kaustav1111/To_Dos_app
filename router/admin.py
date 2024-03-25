from fastapi import FastAPI, APIRouter, Depends, Path, HTTPException, status
from models import Todos
from database import Sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import decode_jwt_token
import warnings
warnings.filterwarnings("ignore")

router = APIRouter(
    prefix="/admin",
    tags=["admins"]
)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(decode_jwt_token)]



@router.get("/admin_read_all_todos", status_code=status.HTTP_200_OK)
def admin_read_todos(user : user_dependency,
               active_db : db_dependency):
    if user is None or str.lower(user.get('role'))!="admin":
        raise HTTPException(status_code=404 , detail="Authentication Error")
    return active_db.query(Todos).all()



@router.put("/admin_delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_todo(user : user_dependency, active_db : db_dependency, todo_id : int):
    if user is None or str.lower(user.get('role'))!="admin":
        raise HTTPException(status_code=404 , detail="Authentication Error")
    todo_model = active_db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404 , detail="Todo not found")
    active_db.query(Todos).filter(Todos.id == todo_id).delete()
    active_db.commit()

