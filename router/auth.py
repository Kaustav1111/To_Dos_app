from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import Sessionlocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose.exceptions import JWTError
from jose import jwt
from datetime import datetime , timedelta
from starlette import status
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import warnings
warnings.filterwarnings("ignore")

SECRET_KEY = "999c884f7fbfbe2c25497bf184c3323a98eabeee302842c5f51292a6773a2f72"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory='templates')

bcrypt_context = CryptContext(schemes=['bcrypt'])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

router = APIRouter(prefix='/auth',
                   tags=['auths'])



class LoginForm:
    def __init__(self , request: Request):
        self.request : Request = request
        self.username : Optional[str] = None
        self.password : Optional[str] = None
    
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")



def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()



def authenticate_user(username : str, password : str, db):
    user = db.query(Users).filter(Users.username == username).first()
    print(type(user))
    if not user:
        return False
    elif bcrypt_context.verify(password, user.hashed_password):
        return user
    return False



def create_jwt(username : str , user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub' : username,
              'id' : user_id,
              'role' : role
             }
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



async def decode_jwt_token(request : Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token , SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username : str = payload.get('sub')
        user_id : int = payload.get('id')
        role : str = payload.get('role')
        if username is None or user_id is None:
            logout(request)
        return {'username' : username , 'id' : user_id , 'role' : role}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate")



@router.post("/token")
async def user_authentication_status(response : Response, form_input : Annotated[OAuth2PasswordRequestForm, Depends()],
                               db : Session = Depends(get_db)):
    user_data = authenticate_user(form_input.username, form_input.password, db)
    if user_data:
        token = create_jwt(user_data.username, user_data.id, user_data.role,  timedelta(minutes=60))
        response.set_cookie(key="access_token", value=token, httponly=True)
        return True
    else:
        return False



@router.get("/login" , response_class=HTMLResponse)
async def login_page_request(request : Request):
    return templates.TemplateResponse("login.html", {'request' : request})

@router.post("/login" , response_class=HTMLResponse)
async def user_login(request : Request, db : Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos/read_todo" , status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await user_authentication_status(response=response, form_input=form, db=db)
        if not validate_user_cookie:
            msg =" Invalid Username or Password"
            return templates.TemplateResponse("login.html" , {'request' : request , 'msg' : msg})
        return response

    except HTTPException:
        msg = "Unkown Error"
        return templates.TemplateResponse("login.html" , {'request' : request , 'msg' : msg})
    


@router.get("/logout" , response_class=HTMLResponse)
async def logout(request : Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html" , {'request' : request , 'msg' : msg})
    response.delete_cookie(key="access_token")
    return response



@router.get("/register" , response_class=HTMLResponse)
async def load_new_user_template(request : Request):
    return templates.TemplateResponse("register.html", {'request' : request})

@router.post("/register" , response_class=HTMLResponse)
async def creating_new_user(request : Request, email : str = Form(...), username : str = Form(...), lastname : str = Form(...),
                            firstname : str = Form(...), password : str = Form(...), password2 : str =Form(...),
                            db : Session = Depends(get_db)):
    validate1 = db.query(Users).filter(Users.username == username).first()
    validate2 = db.query(Users).filter(Users.email == email).first()
    if password != password2 or validate1 is not None or validate2 is not None:
        msg = "Invalid User Request"
        response = templates.TemplateResponse("register.html" , {"request" : request , "msg" : msg})
        return response
    user_model = Users()
    user_model.username = username
    user_model.email = email
    user_model.firstname = firstname
    user_model.lastname = lastname
    user_model.hashed_password = bcrypt_context.hash(password)
    user_model.is_active = True
    
    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html" , {"request" : request , "msg" : msg})






