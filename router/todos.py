from fastapi import APIRouter, Depends, Path, HTTPException, status, Request, Form
from models import Todos
from database import Sessionlocal
from sqlalchemy.orm import Session
from .auth import decode_jwt_token
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status
import warnings
warnings.filterwarnings("ignore")

router = APIRouter(prefix="/todos",
                   tags=["todos"])


templates = Jinja2Templates(directory="templates")


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/read_todo", response_class=HTMLResponse)
async def user_read_all(request : Request, db: Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    return templates.TemplateResponse('home.html' , {'request' : request , 'todos' : todos , 'user' : user})



@router.get("/add_todo", response_class=HTMLResponse)
async def add_todo(request : Request):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('add-todo.html' , {'request' : request , 'user' : user})

@router.post("/add_todo", response_class=HTMLResponse)
async def create_todo(request : Request, title : str = Form(...), description : str = Form(...),
                priority: int = Form(...), db : Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    todos_model = Todos()
    todos_model.title = title
    todos_model.description = description
    todos_model.priority = priority
    todos_model.complete = False
    todos_model.owner_id = user.get('id')

    db.add(todos_model)
    db.commit()

    return RedirectResponse(url='/todos/read_todo' , status_code=status.HTTP_302_FOUND)

    

@router.get("/edit_todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request : Request, todo_id : int, db : Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse('edit-todo.html' , {'request' : request, 'todo' : todo, 'user' : user})

@router.post("/edit_todo/{todo_id}" , response_class=HTMLResponse)
async def editing_todo(request : Request, todo_id : int, title : str = Form(...), description : str = Form(...), 
                 priority: int = Form(...), db : Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/todos/read_todo' , status_code=status.HTTP_302_FOUND)



@router.get("/delete_todo/{todo_id}" , response_class=HTMLResponse)
async def delete_todo(request : Request, todo_id : int, db : Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    
    if todo_model is None:
        return RedirectResponse(url="/todos/read_todo" , status_code=status.HTTP_302_FOUND)
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse(url="/todos/read_todo" , status_code=status.HTTP_302_FOUND)



@router.get("/complete_todo/{todo_id}" , response_class=HTMLResponse)
async def complete_todo(request : Request, todo_id : int, db : Session = Depends(get_db)):
    user = await decode_jwt_token(request)
    if user is None:
        return RedirectResponse(url="/auth/login" , status_code=status.HTTP_302_FOUND)
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_model.complete = not todo_model.complete
    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos/read_todo" , status_code=status.HTTP_302_FOUND)