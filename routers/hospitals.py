from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
)
from sqlalchemy.orm import Session
import database, schemas, models
from JWTtoken import get_admin_user

router = APIRouter(prefix="/hospital", tags=["Hospital"])
get_db = database.get_db


# Get all hospitals
@router.get("/", response_model=list[schemas.Hospital])
async def get_all_hospitals(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_admin_user),
):
    hospitals = db.query(models.Hospital).all()
    return hospitals


# Get hospital by id
@router.get("/{hospital_id}", response_model=schemas.Hospital)
async def get_hospital_by_id(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_admin_user),
):
    hospital = (
        db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    )
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )
    return hospital


# Create a hospital
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_hospital(
    hospital: schemas.HospitalCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_admin_user),
):
    new_hospital = models.Hospital(
        name=hospital.name,
        address=hospital.address,
        phone=hospital.phone,
        email=hospital.email,
    )
    db.add(new_hospital)
    db.commit()
    db.refresh(new_hospital)
    return new_hospital


# Update a hospital
@router.put("/{hospital_id}", response_model=schemas.Hospital)
async def update_hospital(
    hospital_id: int,
    updated_hospital: schemas.Hospital,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_admin_user),
):
    hospital = (
        db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    )
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )

    hospital.name = updated_hospital.name
    hospital.address = updated_hospital.address
    hospital.phone = updated_hospital.phone
    hospital.email = updated_hospital.email

    db.commit()
    db.refresh(hospital)
    return hospital


# Delete a hospital
@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_admin_user),
):
    hospital = (
        db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    )
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )

    db.delete(hospital)
    db.commit()
    return {"detail": "Hospital deleted"}
