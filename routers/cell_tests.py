from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    UploadFile,
    File,
    Query,
)
from sqlalchemy.orm import Session
import uuid
import database, schemas, models
from JWTtoken import get_current_user
from pathlib import Path

router = APIRouter(prefix="/hospital", tags=["Cell-test"])
get_db = database.get_db


# Create a cell test for a patient
@router.post(
    "/{hospital_id}/patients/{patient_id}/cell_tests", response_model=schemas.CellTest
)
async def create_cell_test_for_patient(
    hospital_id: int,
    patient_id: str,
    cell_test: schemas.CellTestCreate,
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

    db_cell_test = models.CellTest(
        title=cell_test.title,
        description=cell_test.description,
        updated_at=cell_test.updated_at,
        created_at=cell_test.created_at,
        detection_status=cell_test.detection_status,
        patient_id=patient_id,
    )
    db.add(db_cell_test)
    db.commit()
    db.refresh(db_cell_test)
    return db_cell_test


def save_image(file: UploadFile, upload_dir: Path):
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True)

    # Generate a unique filename using uuid
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    file_path = upload_dir / unique_filename
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())
    return file_path


@router.post(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/data_images",
    response_model=schemas.CellTestImageDataCreate,
)
async def upload_image(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        # Directory where images will be stored
        upload_dir = Path("media/images/test_images")

        # Save the uploaded image to the specified directory with a unique name
        saved_image_path = save_image(file, upload_dir)

        # Create an entry in the database for the uploaded image
        db_image = models.CellTestImageData(
            image=str(saved_image_path),
            cell_test_id=cell_test_id,  # Set the cell_test_id here
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")


# Create a result for a cell test
@router.post(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/results",
    response_model=schemas.Result,
)
async def create_result_for_cell_test(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    result: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if hospital exists
    db_hospital = (
        db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    )
    if not db_hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )

    # Check if patient exists within the hospital
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

    # Check if cell test exists for the patient
    db_cell_test = (
        db.query(models.CellTest)
        .filter(
            models.CellTest.id == cell_test_id, models.CellTest.patient_id == patient_id
        )
        .first()
    )
    if not db_cell_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cell test not found"
        )

    # Check if the current user has permission to create a result for this cell test
    if not current_user.is_admin and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    # Create the result
    db_result = models.Result(
        description=result.description,
        created_at=result.created_at,
        celltest_id=cell_test_id,
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    # Ensure cell_test_id is included in the response
    return schemas.Result(
        id=db_result.id,
        description=db_result.description,
        created_at=db_result.created_at,
        cell_test_id=db_result.celltest_id,
    )