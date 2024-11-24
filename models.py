from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    Date,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from database import Base


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    address = Column(String)
    blood_group = Column(String)
    gender = Column(String)
    contact_no = Column(String)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_hospital_admin = Column(Boolean, default=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    hospital = relationship("Hospital", back_populates="users")


# Password Reset Token model
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Hospital model
class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(254), nullable=True)

    users = relationship("User", back_populates="hospital")
    patients = relationship("Patient", back_populates="hospital")


# Patient model
class Patient(Base):
    __tablename__ = "lab_patient"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    phone = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    address = relationship("Address", uselist=False, back_populates="patient")
    cell_tests = relationship("CellTest", back_populates="patient")
    hospital = relationship("Hospital", back_populates="patients")


# Address model
class Address(Base):
    __tablename__ = "lab_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    patient_id = Column(
        UUID(as_uuid=True), ForeignKey("lab_patient.id"), nullable=False, unique=True
    )

    patient = relationship("Patient", back_populates="address")


# Cell Test model
class CellTest(Base):
    __tablename__ = "lab_celltest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    detection_status = Column(String(255), nullable=False)
    patient_id = Column(
        UUID(as_uuid=True), ForeignKey("lab_patient.id"), nullable=False
    )

    patient = relationship("Patient", back_populates="cell_tests")
    results = relationship("Result", back_populates="cell_test")
    cell_test_images = relationship("CellTestImageData", back_populates="cell_test")


# Result model
class Result(Base):
    __tablename__ = "lab_result"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    celltest_id = Column(
        UUID(as_uuid=True), ForeignKey("lab_celltest.id"), nullable=False
    )

    cell_test = relationship("CellTest", back_populates="results")
    result_images = relationship("ResultImageData", back_populates="result")


# Cell Test Image Data model
class CellTestImageData(Base):
    __tablename__ = "lab_celltestimagedata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String(100), nullable=False)
    cell_test_id = Column(
        UUID(as_uuid=True), ForeignKey("lab_celltest.id"), nullable=False
    )

    cell_test = relationship("CellTest", back_populates="cell_test_images")


# Result Image Data model
class ResultImageData(Base):
    __tablename__ = "lab_resultimagedata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String(100), nullable=False)
    result_id = Column(UUID(as_uuid=True), ForeignKey("lab_result.id"), nullable=False)

    result = relationship("Result", back_populates="result_images")
