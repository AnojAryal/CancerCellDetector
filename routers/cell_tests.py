from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Query,
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


# get cell_tests
@router.get(
    "/{hospital_id}/patients/{patient_id}/cell_tests",
    response_model=List[schemas.CellTest],
)
async def get_cell_tests_for_patient(
    hospital_id: int,
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
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

        cell_tests = (
            db.query(models.CellTest)
            .filter(models.CellTest.patient_id == patient_id)
            .all()
        )

        return cell_tests
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cell tests: {e}",
        )


# update cell_test
@router.put(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}",
    response_model=schemas.CellTest,
)
async def update_cell_test_for_patient(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    cell_test_update: schemas.CellTestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
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

        db_cell_test = (
            db.query(models.CellTest)
            .filter(
                models.CellTest.id == cell_test_id,
                models.CellTest.patient_id == patient_id,
            )
            .first()
        )
        if not db_cell_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cell test not found"
            )

        db_cell_test.title = cell_test_update.title
        db_cell_test.description = cell_test_update.description
        db_cell_test.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_cell_test)

        return db_cell_test
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cell test: {e}",
        )


# delete cell_test
@router.delete(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}",
    response_model=schemas.CellTest,
)
async def delete_cell_test_for_patient(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
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

        db_cell_test = (
            db.query(models.CellTest)
            .filter(
                models.CellTest.id == cell_test_id,
                models.CellTest.patient_id == patient_id,
            )
            .first()
        )
        if not db_cell_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cell test not found"
            )

        # Delete the cell test
        db.delete(db_cell_test)
        db.commit()

        return db_cell_test
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete cell test: {e}",
        )


# post image data for celltest
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
        hospital = (
            db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
        )
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
            )
        patient = (
            db.query(models.Patient)
            .filter(
                models.Patient.id == patient_id,
                models.Patient.hospital_id == hospital_id,
            )
            .first()
        )
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )
        cell_test = (
            db.query(models.CellTest)
            .filter(
                models.CellTest.id == cell_test_id,
                models.CellTest.patient_id == patient_id,
            )
            .first()
        )
        if not cell_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cell test not found"
            )

        upload_dir = Path("media/images/test_images")

        saved_image_path = save_image(file, upload_dir)

        db_image = models.CellTestImageData(
            image=str(saved_image_path),
            cell_test_id=cell_test_id,
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e}",
        )


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

        if not current_user.is_admin and current_user.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )

        if not current_user.is_admin and current_user.patient_id != patient_id:
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


# retrive results
@router.get(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/results",
    response_model=List[schemas.Result],
)
async def get_results_for_cell_test(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        # Check user permissions
        if not current_user.is_admin and current_user.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )

        db_hospital = (
            db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
        )

        if not db_hospital or (
            not current_user.is_admin and current_user.hospital_id != hospital_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="hospital id mismatch"
            )

        results = (
            db.query(models.Result)
            .filter(models.Result.celltest_id == cell_test_id)
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=404, detail="No results found for this cell test ID"
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {e}")


# post result image
@router.post(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/results/{result_id}/result-images/",
    response_model=schemas.ResultImageDataCreate,
)
async def upload_result_image(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    result_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:

        hospital = (
            db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
        )
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
            )

        patient = (
            db.query(models.Patient)
            .filter(
                models.Patient.id == patient_id,
                models.Patient.hospital_id == hospital_id,
            )
            .first()
        )
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )

        cell_test = (
            db.query(models.CellTest)
            .filter(
                models.CellTest.id == cell_test_id,
                models.CellTest.patient_id == patient_id,
            )
            .first()
        )
        if not cell_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cell test not found"
            )

        result = (
            db.query(models.Result)
            .filter(
                models.Result.id == result_id,
                models.Result.celltest_id == cell_test_id,
            )
            .first()
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
            )

        upload_dir = Path("media/images/result_images")

        saved_image_path = save_image(file, upload_dir)

        db_image = models.ResultImageData(
            image=str(saved_image_path),
            result_id=result_id,
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {e}",
        )


# get result images
@router.get(
    "/{hospital_id}/patients/{patient_id}/cell_tests/{cell_test_id}/results/{result_id}/result-images/",
    response_model=List[schemas.ResultImageData],
)
async def get_result_images(
    hospital_id: int,
    patient_id: str,
    cell_test_id: str,
    result_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        result_images = (
            db.query(models.ResultImageData)
            .filter(models.ResultImageData.result_id == result_id)
            .all()
        )

        if not result_images:
            raise HTTPException(
                status_code=404, detail="No images found for this result ID"
            )

        return result_images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {e}")
