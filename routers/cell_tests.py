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
