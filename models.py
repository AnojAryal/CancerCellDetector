from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base
from sqlalchemy.orm import relationship



class User(Base):
    tablename = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    address = Column(String)
    blood_group = Column(String)
    gender = Column(String)
    contact_no = Column(String)
    hashed_password = Column(String)

    login_info = relationship("UserLogin", uselist=False, back_populates="user")

class UserLogin(Base):
    __tablename = "user_login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="login_info")