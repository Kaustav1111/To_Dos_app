from database import Base 
from sqlalchemy import Column , Integer , String , Boolean, ForeignKey
import warnings
warnings.filterwarnings("ignore")

class Users(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer , primary_key=True , index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

# So, when you define a class todos with Base as its base class, it means that todos inherits properties and methods 
# from the Base class. This allows todos to access and use the attributes and methods defined in Base, potentially
# extending or customizing its behavior.






    