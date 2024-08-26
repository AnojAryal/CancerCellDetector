from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    File,
    UploadFile,
)
from datetime import datetime
from sqlalchemy.orm import Session
import database, schemas, models
from JWTtoken import get_current_user
from pathlib import Path
from typing import List
from save_image import save_image

router = APIRouter(prefix="/hospital", tags=["Cell-test"])
get_db = database.get_db


# Endpoint to retrieve all images associated with a specific cell test ID
@router.get(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/data_images",
    response_model=List[schemas.CellTestImageData],
)
async def get_cell_test_images(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        # Check if the user is an admin or belongs to the same hospital
        if not current_user.is_admin and current_user.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )

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
                models.Patient.id == patient_id,
                models.Patient.hospital_id == hospital_id,
            )
            .first()
        )
        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )

        # Fetch cell test images associated with the specific cell test ID
        cell_test_images = (
            db.query(models.CellTestImageData)
            .filter(models.CellTestImageData.cell_test_id == cell_test_id)
            .all()
        )

        if not cell_test_images:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No images found for this cell test ID",
            )

        return cell_test_images
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve images: {e}",
        )
