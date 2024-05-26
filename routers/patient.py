from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import database, schemas, models


router = APIRouter(prefix="/patient", tags=["Patient"])
get_db = database.get_db


@router.post(
    "/", response_model=schemas.PatientCreate, status_code=status.HTTP_201_CREATED
)
def create_patient(patient_data: schemas.PatientCreate, db: Session = Depends(get_db)):

    new_patient = models.Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        phone=patient_data.phone,
        birth_date=patient_data.birth_date,
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@router.get("/{id}")
def get_patient_by_id(id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with ID {id} not found")
    return patient
