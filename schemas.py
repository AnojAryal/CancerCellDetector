from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import date, datetime


# Base model for User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    address: str
    blood_group: str
    gender: str
    contact_no: str


# Model for creating a user with password
class UserCreate(UserBase):
    password: str


# User model
class User(UserBase):
    id: int
    is_verified: bool

    class Config:
        from_attrs = True


# Login model
class Login(BaseModel):
    username: str
    password: str


# Token model
class Token(BaseModel):
    access_token: str
    token_type: str


# Token data model
class TokenData(BaseModel):
    username: Optional[str] = None


# Model for requesting password reset
class PasswordResetRequest(BaseModel):
    email: str


# Model for confirming password reset
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# Base model for Patient
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    birth_date: date


# Model for creating a patient
class PatientCreate(PatientBase):
    pass


# Patient model
class Patient(PatientBase):
    id: UUID4

    class Config:
        from_attrs = True


# Base model for Address
class AddressBase(BaseModel):
    street: str
    city: str
    patient_id: UUID4


# Model for creating an address
class AddressCreate(AddressBase):
    pass


# Address model
class Address(AddressBase):
    id: int

    class Config:
        from_attrs = True


# Base model for Cell Test
class CellTestBase(BaseModel):
    title: str
    description: Optional[str]
    updated_at: datetime
    created_at: datetime
    detection_status: str
    patient_id: UUID4


# Model for creating a cell test
class CellTestCreate(CellTestBase):
    pass


# Cell Test model
class CellTest(CellTestBase):
    id: UUID4

    class Config:
        from_attrs = True


# Base model for Result
class ResultBase(BaseModel):
    description: Optional[str]
    created_at: date
    celltest_id: UUID4


# Model for creating a result
class ResultCreate(ResultBase):
    pass


# Result model
class Result(ResultBase):
    id: UUID4

    class Config:
        from_attrs = True


# Base model for Cell Test Image Data
class CellTestImageDataBase(BaseModel):
    image: str
    cell_test_id: UUID4


# Model for creating cell test image data
class CellTestImageDataCreate(CellTestImageDataBase):
    pass


# Cell Test Image Data model
class CellTestImageData(CellTestImageDataBase):
    id: int

    class Config:
        from_attrs = True


# Base model for Result Image Data
class ResultImageDataBase(BaseModel):
    image: str
    result_id: UUID4


# Model for creating result image data
class ResultImageDataCreate(ResultImageDataBase):
    pass


# Result Image Data model
class ResultImageData(ResultImageDataBase):
    id: int

    class Config:
        from_attrs = True
