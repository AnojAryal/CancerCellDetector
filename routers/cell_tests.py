from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
import database, schemas, models


router = APIRouter(prefix="/cell_test", tags=["Cell_test"])
get_db = database.get_db


@router.post("/", response_model=schemas.CellTest, status_code=status.HTTP_201_CREATED)
def create_cellTest(
    cellTest_data: schemas.CellTestCreate, db: Session = Depends(get_db)
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


@router.get("/{id}")
def get_cellTest_by_id(id: UUID, db: Session = Depends(get_db)):
    cell_test = db.query(models.CellTest).filter(models.CellTest.id == id).first()
    if not cell_test:
        raise HTTPException(status_code=404, detail=f"Test with ID {id} not found")
    return cell_test


@router.post(
    "/result/", response_model=schemas.Result, status_code=status.HTTP_201_CREATED
)
def create_result(result_data: schemas.ResultCreate, db: Session = Depends(get_db)):

    new_result = models.Result(
        description=result_data.description,
        created_at=result_data.created_at,
        celltest_id=result_data.celltest_id,
    )

    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return new_result


@router.get("/result/{id}")
def get_testResult_by_id(id: UUID, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter(models.Result.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Result with ID {id} not found")
    return result


@router.post(
    "/image_data/",
    response_model=schemas.CellTestImageData,
    status_code=status.HTTP_201_CREATED,
)
def test_image(
    cellTestImage_data: schemas.CellTestImageDataCreate, db: Session = Depends(get_db)
):

    new_ImageData = models.CellTestImageData(
        image=cellTestImage_data.image,
        cell_test_id=cellTestImage_data.cell_test_id,
    )

    db.add(new_ImageData)
    db.commit()
    db.refresh(new_ImageData)

    return new_ImageData


@router.get("/image_data/{id}")
def get_testimagedata_by_id(id: int, db: Session = Depends(get_db)):
    test_image = (
        db.query(models.CellTestImageData)
        .filter(models.CellTestImageData.id == id)
        .first()
    )
    if not test_image:
        raise HTTPException(
            status_code=404, detail=f"test_image with ID {id} not found"
        )
    return test_image


@router.post(
    "/result_data/",
    response_model=schemas.ResultImageData,
    status_code=status.HTTP_201_CREATED,
)
def test_result(
    cellTestResult_data: schemas.ResultImageDataCreate, db: Session = Depends(get_db)
):

    new_resultData = models.ResultImageData(
        image=cellTestResult_data.image,
        result_id=cellTestResult_data.result_id,
    )

    db.add(new_resultData)
    db.commit()
    db.refresh(new_resultData)

    return new_resultData


@router.get("/result_data/{id}")
def get_testresultdata_by_id(id: int, db: Session = Depends(get_db)):
    test_result = (
        db.query(models.ResultImageData).filter(models.ResultImageData.id == id).first()
    )
    if not test_result:
        raise HTTPException(
            status_code=404, detail=f"test_result with ID {id} not found"
        )
    return test_result
