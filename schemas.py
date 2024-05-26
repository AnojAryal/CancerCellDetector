from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import date, datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    address: str
    blood_group: str
    gender: str
    contact_no: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_verified: bool

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    birth_date: date


class PatientCreate(PatientBase):
    pass


class Patient(PatientBase):
    id: UUID4

    class Config:
        orm_mode = True


class AddressBase(BaseModel):
    street: str
    city: str
    patient_id: UUID4


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: int

    class Config:
        orm_mode = True


class CellTestBase(BaseModel):
    title: str
    description: Optional[str]
    updated_at: datetime
    created_at: datetime
    detection_status: str
    patient_id: UUID4


class CellTestCreate(CellTestBase):
    pass


class CellTest(CellTestBase):
    id: UUID4

    class Config:
        orm_mode = True


class ResultBase(BaseModel):
    description: Optional[str]
    created_at: date
    celltest_id: UUID4


class ResultCreate(ResultBase):
    pass


class Result(ResultBase):
    id: UUID4

    class Config:
        orm_mode = True


class CellTestImageDataBase(BaseModel):
    image: str
    cell_test_id: UUID4


class CellTestImageDataCreate(CellTestImageDataBase):
    pass


class CellTestImageData(CellTestImageDataBase):
    id: int

    class Config:
        orm_mode = True


class ResultImageDataBase(BaseModel):
    image: str
    result_id: UUID4


class ResultImageDataCreate(ResultImageDataBase):
    pass


class ResultImageData(ResultImageDataBase):
    id: int

    class Config:
        orm_mode = True
