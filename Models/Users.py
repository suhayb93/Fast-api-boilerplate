from Database import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__= 'users'

    id = Column(Integer,primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String)
    password_hash = Column(String)
