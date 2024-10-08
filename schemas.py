from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


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
    is_admin: Optional[bool] = False
    is_hospital_admin: Optional[bool] = False
    hospital_id: Optional[int] = None

    # Override to only include hospital_id if the user is an admin
    @property
    def dict(self):
        if self.is_admin:
            return super().dict()
        else:
            return {k: v for k, v in super().dict().items() if k != "hospital_id"}


# User model
class User(UserBase):
    id: int
    is_verified: bool
    is_admin: bool
    is_hospital_admin: bool
    hospital_id: Optional[int]

    class Config:
        from_attributes = True


# user update model
class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    gender: Optional[str] = None
    contact_no: Optional[str] = None
    is_admin: Optional[bool] = None
    is_hospital_admin: Optional[bool] = None
    hospital_id: Optional[int] = None


# user profile
class UserProfile(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    address: str
    blood_group: str
    gender: str
    contact_no: str

    class Config:
        form_attributes = True


# user update model
class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    gender: Optional[str] = None
    contact_no: Optional[str] = None


# Model for password reset token
class PasswordResetRequest(BaseModel):
    email: EmailStr
    token: str
    used: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Base model for Hospital
class HospitalBase(BaseModel):
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]


# Model for creating a hospital
class HospitalCreate(HospitalBase):
    pass


# Hospital model
class Hospital(HospitalBase):
    id: int
    users: List[User] = []
    patients: List["Patient"] = []

    class Config:
        from_attributes = True


# Base model for Patient
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    birth_date: date
    hospital_id: Optional[int]


# Model for creating a patient
class PatientCreate(PatientBase):
    pass


# Patient model
class Patient(PatientBase):
    id: UUID

    class Config:
        form_attributes = True


# Base model for Address
class AddressBase(BaseModel):
    street: str
    city: str


# Model for creating an address
class AddressGet(AddressBase):
    id: int
    street: str
    city: str


# Model for creating an address
class AddressCreate(AddressBase):
    patient_id: UUID


# Model for updating an address
class AddressUpdate(AddressBase):
    street: str = None
    city: str = None


# Address model
class Address(AddressBase):
    id: int
    patient_id: UUID

    class Config:
        form_attributes = True


# Base model for Cell Test
class CellTestBase(BaseModel):
    title: str
    description: Optional[str]
    updated_at: datetime
    created_at: datetime
    detection_status: str


# Base model for Cell Test
class CellTestFetch(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    updated_at: datetime
    created_at: datetime
    detection_status: str


# Model for creating a cell test
class CellTestCreate(CellTestBase):
    pass


# Cell Test model
class CellTest(CellTestBase):
    id: UUID
    patient_id: UUID

    class Config:
        from_attributes = True


class PatientWithAddressAndCellTests(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    birth_date: datetime
    hospital_id: Optional[int] = None
    address: Optional[AddressGet] = None
    cell_tests: Optional[List[CellTestFetch]] = []

    class Config:
        form_attributes = True


# Base model for Cell Test Image Data
class CellTestImageData(BaseModel):
    image: str
    cell_test_id: UUID


# Model for creating cell test image data
class CellTestImageDataCreate(CellTestImageData):
    pass


# Cell Test Image Data model
class CellTestImageData(CellTestImageData):
    id: int

    class Config:
        from_attributes = True


# Base model for Result Image Data
class ResultImageData(BaseModel):
    image: str
    result_id: UUID


# Model for creating result image data
class ResultImageDataCreate(ResultImageData):
    pass


# Result Image Data model
class ResultImageData(ResultImageData):
    id: int

    class Config:
        from_attributes = True


# Base model for Result
class ResultBase(BaseModel):
    description: Optional[str]
    created_at: date
    celltest_id: UUID
    result_images: Optional[List[ResultImageData]] = []


# Model for creating a result
class ResultCreate(ResultBase):
    pass


# Result model
class Result(ResultBase):
    id: UUID

    class Config:
        from_attributes = True


class CellTestFetch(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    updated_at: datetime
    created_at: datetime
    detection_status: str
    results: Optional[List[Result]] = []


# Changing the password
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
