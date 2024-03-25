from fastapi import FastAPI
import models
from database import engine
from router import auth, todos, admin, users
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
import warnings
warnings.filterwarnings("ignore")

models.Base.metadata.create_all(bind=engine)
# This line calls the create_all method on the metadata associated with your SQLAlchemy base class (Base). 
# The bind parameter specifies the engine to use for database interaction. This function creates all the tables defined 
# in your SQLAlchemy models in the connected database.

# By calling this function when your FastAPI application starts, you ensure that the necessary database tables are 
# created if they don't exist already. This is a common practice to ensure that your application's database schema matches
# your SQLAlchemy models.

app = FastAPI()

@app.get("/")
async def root():
    return RedirectResponse(url="/todos/read_todo", status_code=status.HTTP_302_FOUND)

app.mount("/static" , StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)