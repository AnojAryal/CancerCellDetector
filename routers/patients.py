from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
import database, schemas, models
from JWTtoken import get_current_user

router = APIRouter(prefix="/patient", tags=["Patient"])
get_db = database.get_db


# Create a new patient
@router.post(
    "/", response_model=schemas.PatientCreate, status_code=status.HTTP_201_CREATED
)
def create_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.hospital_id != patient_data.hospital_id:
        raise HTTPException(
            status_code=403, detail="Current userID and HospitalID don't match"
        )

    new_patient = models.Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        phone=patient_data.phone,
        birth_date=patient_data.birth_date,
        hospital_id = patient_data.hospital_id
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# Retrieve patients by their ID
@router.get("/{patient_id}")
def get_patient_by_id(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with ID {id} not found")
    return patient


@router.post(
    "/{patient_id}/address",
    response_model=schemas.Address,
    status_code=status.HTTP_201_CREATED,
)
def create_address_for_patient(
    patient_id: UUID,
    address_data: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if the current user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    # Check if the patient exists
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    new_address = models.Address(
        street=address_data.street,
        city=address_data.city,
        patient_id=patient_id,
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return new_address


# Retrieve address by patient ID
@router.get("/{patient_id}/address")
def get_address_by_patient_id(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    address = (
        db.query(models.Address).filter(models.Address.patient_id == patient_id).all()
    )
    if not address:
        raise HTTPException(
            status_code=404,
            detail=f"Address for patient with ID {patient_id} not found",
        )
    return address


# Retrieve an address for a patient by patient ID and address ID
@router.get("/{patient_id}/address/{address_id}", response_model=schemas.Address)
def get_address_for_patient(
    patient_id: str,
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    address = (
        db.query(models.Address)
        .filter(
            models.Address.id == address_id, models.Address.patient_id == patient_id
        )
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=404,
            detail=f"Address with ID {address_id} for patient with ID {patient_id} not found",
        )

    return address
