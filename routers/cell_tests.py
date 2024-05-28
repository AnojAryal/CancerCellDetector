from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
import database, schemas, models
from JWTtoken import get_current_user


router = APIRouter(prefix="/cell_test", tags=["Cell_test"])
get_db = database.get_db


# Create a new cell test
@router.post("/", response_model=schemas.CellTest, status_code=status.HTTP_201_CREATED)
def create_cell_test(
    cellTest_data: schemas.CellTestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    new_cellTest = models.CellTest(
        title=cellTest_data.title,
        description=cellTest_data.description,
        updated_at=cellTest_data.updated_at,
        created_at=cellTest_data.created_at,
        detection_status=cellTest_data.detection_status,
        patient_id=cellTest_data.patient_id,
    )

    db.add(new_cellTest)
    db.commit()
    db.refresh(new_cellTest)

    return new_cellTest


# Retrieve a cell test by its ID
@router.get("/{cell_test_id}")
def get_cell_test_by_id(
    cell_test_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cell_test = (
        db.query(models.CellTest).filter(models.CellTest.id == cell_test_id).first()
    )
    if not cell_test:
        raise HTTPException(status_code=404, detail=f"Test with ID {id} not found")
    return cell_test


# Create a new result
@router.post(
    "/{cell_test_id}/result",
    response_model=schemas.Result,
    status_code=status.HTTP_201_CREATED,
)
def create_result(
    cell_test_id: UUID,
    result_data: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if a result already exists for the given cell_test_id
    existing_result = (
        db.query(models.Result)
        .filter(models.Result.celltest_id == cell_test_id)
        .first()
    )
    if existing_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Result for this cell test ID already exists",
        )

    new_result = models.Result(
        description=result_data.description,
        created_at=result_data.created_at,
        celltest_id=cell_test_id,
    )

    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return new_result


# Retrieve a result by its ID
@router.get("/{cell_test_id}/result")
def get_test_result_by_id(
    cell_test_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = (
        db.query(models.Result)
        .filter(models.Result.celltest_id == cell_test_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Result with ID {id} not found")
    return result


@router.post(
    "/{cell_test_id}/image_data",
    response_model=schemas.CellTestImageData,
    status_code=status.HTTP_201_CREATED,
)
def test_image(
    cell_test_id: UUID,
    cellTestImage_data: schemas.CellTestImageDataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Checking if image data already exists for the given cell_test_id
    existing_image_data = (
        db.query(models.CellTestImageData)
        .filter(models.CellTestImageData.cell_test_id == cell_test_id)
        .first()
    )
    if existing_image_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image data for this cell test ID already exists",
        )

    new_image_data = models.CellTestImageData(
        image=cellTestImage_data.image,
        cell_test_id=cell_test_id,
    )

    db.add(new_image_data)
    db.commit()
    db.refresh(new_image_data)

    return new_image_data


# Retrieve test image data by its ID
@router.get("/{cell_test_id}/image_data")
def get_test_image_data_by_id(
    cell_test_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    test_image = (
        db.query(models.CellTestImageData)
        .filter(models.CellTestImageData.cell_test_id == cell_test_id)
        .first()
    )
    if not test_image:
        raise HTTPException(
            status_code=404, detail=f"test_image with ID {id} not found"
        )
    return test_image


# Create a new cell test result
@router.post(
    "/{result_id}/result_data",
    response_model=schemas.ResultImageData,
    status_code=status.HTTP_201_CREATED,
)
def create_result_data(
    result_id: UUID,
    result_image_data: schemas.ResultImageDataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Checking if the result exists
    existing_result = (
        db.query(models.Result).filter(models.Result.id == result_id).first()
    )
    if not existing_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found",
        )

    # Optionally, checking if result data for this result_id already exists
    existing_result_data = (
        db.query(models.ResultImageData)
        .filter(models.ResultImageData.result_id == result_id)
        .first()
    )
    if existing_result_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Result data for this result ID already exists",
        )

    new_result_data = models.ResultImageData(
        image=result_image_data.image,
        result_id=result_id,
    )

    db.add(new_result_data)
    db.commit()
    db.refresh(new_result_data)

    return new_result_data


# Retrive cell test result by its ID
@router.get("{result_id}/result_data")
def get_test_result_data_by_id(
    result_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    test_result = (
        db.query(models.ResultImageData)
        .filter(models.ResultImageData.result_id == result_id)
        .first()
    )
    if not test_result:
        raise HTTPException(
            status_code=404, detail=f"test_result with ID {id} not found"
        )
    return test_result


# Create a new result for a cell test
@router.post(
    "/{cell_test_id}/results/{result_id}/",
    response_model=schemas.Result,
    status_code=status.HTTP_201_CREATED,
)
def create_result_for_cell_test(
    cell_test_id: str,
    result_id: str,
    result_data: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    cell_test = (
        db.query(models.CellTest).filter(models.CellTest.id == cell_test_id).first()
    )
    if not cell_test:
        raise HTTPException(
            status_code=404, detail=f"Cell test with ID {cell_test_id} not found"
        )

    new_result = models.Result(
        description=result_data.description,
        created_at=result_data.created_at,
        celltest_id=cell_test_id,
    )

    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return new_result


# Retrieve a result for a cell test by its ID
@router.get("/{cell_test_id}/results/{result_id}/", response_model=schemas.Result)
def get_result_for_cell_test(
    cell_test_id: str,
    result_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    result = (
        db.query(models.Result)
        .filter(
            models.Result.id == result_id, models.Result.celltest_id == cell_test_id
        )
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Result with ID {result_id} for cell test with ID {cell_test_id} not found",
        )

    return result


# Retrieve images obtained from result
@router.get(
    "/{cell_test_id}/results/{result_id}/result-images/",
    response_model=list[schemas.ResultImageData],
)
def get_result_images_for_result(
    cell_test_id: str,
    result_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result_images = (
        db.query(models.ResultImageData)
        .filter(models.ResultImageData.result_id == result_id)
        .all()
    )
    if not result_images:
        raise HTTPException(
            status_code=404,
            detail=f"No result images found for result with ID {result_id}",
        )

    return result_images


# Retrieve a image by its ID obtained from result
@router.get(
    "/{cell_test_id}/results/{result_id}/result-images/{result_image_id}/",
    response_model=schemas.ResultImageData,
)
def get_result_image(
    cell_test_id: str,
    result_id: str,
    result_image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result_image = (
        db.query(models.ResultImageData)
        .filter(
            models.ResultImageData.id == result_image_id,
            models.ResultImageData.result_id == result_id,
        )
        .first()
    )
    if not result_image:
        raise HTTPException(
            status_code=404,
            detail=f"Result image with ID {result_image_id} for result with ID {result_id} not found",
        )

    return result_image


# Retrieve data images obtained from cell test
@router.get(
    "/{cell_test_id}/data-images/", response_model=list[schemas.CellTestImageData]
)
def get_cell_test_data_images(
    cell_test_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data_images = (
        db.query(models.CellTestImageData)
        .filter(models.CellTestImageData.cell_test_id == cell_test_id)
        .all()
    )
    if not data_images:
        raise HTTPException(
            status_code=404,
            detail=f"No data images found for cell test with ID {cell_test_id}",
        )

    return data_images


# Retrieve a data image by its obtained from cell test
@router.get(
    "/{cell_test_id}/data-images/{data_image_id}/",
    response_model=schemas.CellTestImageData,
)
def get_cell_test_data_image(
    cell_test_id: str,
    data_image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data_image = (
        db.query(models.CellTestImageData)
        .filter(
            models.CellTestImageData.id == data_image_id,
            models.CellTestImageData.cell_test_id == cell_test_id,
        )
        .first()
    )

    if not data_image:
        raise HTTPException(
            status_code=404,
            detail=f"Data image with ID {data_image_id} for cell test with ID {cell_test_id} not found",
        )

    return data_image
