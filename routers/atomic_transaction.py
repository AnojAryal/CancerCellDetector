from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
import requests
from pydantic import ValidationError
from models import CellTestImageData, Result, ResultImageData
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from typing import Any


router = APIRouter(tags=["Atomic-Transaction"])


def send_progress(message: str):
    print(message)


@router.post("/process-cell-test/{cell_test_id}", response_model=Any)
def process_cell_test(cell_test_id: UUID, db: Session = Depends(get_db)):
    try:
        # Retrieve all image paths for the given cell_test_id from the database
        image_data = (
            db.query(CellTestImageData)
            .filter(CellTestImageData.cell_test_id == cell_test_id)
            .all()
        )

        if not image_data:
            return JSONResponse(
                {"error": "No images found for this cell test ID."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Generate URLs from file paths
        base_url = "http://127.0.0.1:8000/"
        image_urls = [base_url + img.image for img in image_data]
        url_list_str = ",".join(image_urls)

        detector_url = "http://127.0.0.1:7000/process-images"
        payload = {"image_urls": url_list_str}

        try:
            response = requests.post(detector_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = f"Error sending images to FastAPI: {str(e)}"
            send_progress(error_message)
            return JSONResponse(
                {"error": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Parse the detector response
        detector_response = response.json()
        cell_test_count = detector_response.get("cell_test_count")
        processed_images = detector_response.get("processed_images")

        if not cell_test_count or not processed_images:
            return JSONResponse(
                {"error": "Invalid response from detector service"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Transaction to save result and processed images
        try:
            with db.begin():
                # Create a new Result object
                result_description = f"Processed {len(processed_images)} images with {cell_test_count} detected cancer cells."
                result = Result(
                    description=result_description, cell_test_id=cell_test_id
                )
                db.add(result)
                db.flush()

                # Attach processed images to the result
                for img_url in processed_images:
                    processed_image = ResultImageData(
                        result_id=result.id, image_url=img_url
                    )
                    db.add(processed_image)

                db.commit()

                # Success response
                return JSONResponse(
                    {
                        "message": "Data stored successfully",
                        "result_id": str(result.id),
                    },
                    status_code=status.HTTP_201_CREATED,
                )

        except SQLAlchemyError as e:
            db.rollback()
            error_message = f"Database error: {str(e)}"
            send_progress(error_message)
            return JSONResponse(
                {"error": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except ValidationError as e:
        send_progress(str(e))
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        send_progress(error_message)
        return JSONResponse(
            {"error": error_message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
