from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
)
from sqlalchemy.orm import Session
from uuid import UUID
import database, schemas, models
from JWTtoken import get_current_user
from typing import List


router = APIRouter(prefix="/hospital", tags=["Patients"])
get_db = database.get_db


# Create a patient for specific hospital
@router.post(
    "/{hospital_id}/patients",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Patient,
)
async def create_patient_for_hospital(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.is_admin:
        # Admin can create a patient for any hospital
        hospital_id_to_use = patient.hospital_id
    else:
        hospital_id_to_use = current_user.hospital_id

    # Check if hospital exists
    db_hospital = (
        db.query(models.Hospital)
        .filter(models.Hospital.id == hospital_id_to_use)
        .first()
    )
    if not db_hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )
    db_patient = models.Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        email=patient.email,
        phone=patient.phone,
        birth_date=patient.birth_date,
        hospital_id=hospital_id_to_use,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


# Retrieve all patients for a hospital
@router.get("/{hospital_id}/patients", response_model=List[schemas.Patient])
async def get_patients_form_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    patients = (
        db.query(models.Patient).filter(models.Patient.hospital_id == hospital_id).all()
    )
    return patients


# Retrieve patients with patient id
@router.get("/{hospital_id}/patients/{patient_id}", response_model=schemas.Patient)
async def get_patients_form_hospital_by_id(
    patient_id: str,
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    patients = (
        db.query(models.Patient)
        .filter(models.Patient.hospital_id == hospital_id)
        .first()
    )
    return patients


# Update a patient
@router.put("/{hospital_id}/patients/{patient_id}", response_model=schemas.Patient)
async def update_patient(
    hospital_id: int,
    patient_id: str,
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_patient = (
        db.query(models.Patient)
        .filter(
            models.Patient.id == patient_id, models.Patient.hospital_id == hospital_id
        )
        .first()
    )
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    for field, value in patient.dict().items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


# Delete a patient
@router.delete("/{hospital_id}/patients/{patient_id}", response_model=schemas.Patient)
async def delete_patient(
    hospital_id: int,
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_patient = (
        db.query(models.Patient)
        .filter(
            models.Patient.id == patient_id, models.Patient.hospital_id == hospital_id
        )
        .first()
    )
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    db.delete(db_patient)
    db.commit()
    return db_patient


# Create an address for a patient
@router.post(
    "/{hospital_id}/patients/{patient_id}/address",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Address,
)
async def create_address_for_patient(
    hospital_id: int,
    patient_id: str,
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_hospital = (
        db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    )
    if not db_hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )
    db_patient = (
        db.query(models.Patient)
        .filter(
            models.Patient.id == patient_id, models.Patient.hospital_id == hospital_id
        )
        .first()
    )
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )
    db_address = models.Address(
        street=address.street,
        city=address.city,
        patient_id=patient_id,
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


# Get addresses for a patient
@router.get(
    "/{hospital_id}/patients/{patient_id}/address/{address_id}",
    response_model=List[schemas.Address],
)
async def get_addresses_for_patient(
    hospital_id: int,
    patient_id: str,
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_patient = (
        db.query(models.Patient)
        .filter(
            models.Patient.id == patient_id, models.Patient.hospital_id == hospital_id
        )
        .first()
    )
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    address = (
        db.query(models.Address).filter(models.Address.patient_id == patient_id).all()
    )
    return address


# Update an address for a patient
@router.put(
    "/{hospital_id}/patients/{patient_id}/address/{address_id}",
    response_model=schemas.Address,
)
async def update_address_for_patient(
    hospital_id: int,
    patient_id: str,
    address_id: int,
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_address = (
        db.query(models.Address)
        .filter(
            models.Address.id == address_id, models.Address.patient_id == patient_id
        )
        .first()
    )
    if db_address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    for field, value in address.dict().items():
        setattr(db_address, field, value)

    db.commit()
    db.refresh(db_address)
    return db_address


# Delete an address for a patient
@router.delete(
    "/{hospital_id}/patients/{patient_id}/address/{address_id}",
    response_model=schemas.Address,
)
async def delete_address_for_patient(
    hospital_id: int,
    patient_id: str,
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_address = (
        db.query(models.Address)
        .filter(
            models.Address.id == address_id, models.Address.patient_id == patient_id
        )
        .first()
    )
    if db_address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    db.delete(db_address)
    db.commit()
    return db_address
