from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    address: str
    blood_group: str
    gender: str
    contact_no: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id:int

    class Config:
        orm_mode:True

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token : str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None