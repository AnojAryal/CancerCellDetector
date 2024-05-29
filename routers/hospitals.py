from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
import database, schemas, models
from JWTtoken import get_admin_user


router = APIRouter(prefix="/hospital", tags=["Hospital"])
get_db = database.get_db


@router.post("/", status_code=status.HTTP_201_CREATED)
async def Create_hospital(
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
