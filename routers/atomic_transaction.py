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

        # Send image URLs to detector service
        detector_url = "http://127.0.0.1:9000/process_images/"
        payload = {"urls": image_urls}

        try:
            response = requests.post(detector_url, json=payload)
            response.raise_for_status()  # Raises an exception for non-2xx status codes
        except requests.exceptions.RequestException as e:
            error_message = f"Error sending images to FastAPI: {str(e)}"
            return JSONResponse(
                {"error": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Parse the detector response
        try:
            detector_response = response.json()
            print("detector response :", detector_response)
        except ValueError as e:
            return JSONResponse(
                {"error": f"Invalid JSON response from detector service: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Extract data from the detector's response
        results = detector_response.get("results", {})
        detected = results.get("detected", {})
        processed_image_urls = results.get("processed_image_urls", [])

        # Validate the extracted data
        if not detected or not processed_image_urls:
            return JSONResponse(
                {"error": "Invalid response structure from detector service"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create the result description with full text for each category
        result_description = (
            f"Background: {detected.get('Background', 0)} pixels detected as background, "
            f"Inflammatory: {detected.get('Inflammatory', 0)} pixels detected as inflammatory cells, "
            f"Cells: {detected.get('cells', 0)} pixels classified as connective/soft tissue cells."
        )

        # Save results and processed images in the database
        try:
            # Create a new Result object
            result = Result(
                description=result_description, celltest_id=cell_test_id
            )
            db.add(result)
            db.flush()

            # Attach processed images to the result
            for img_url in processed_image_urls:
                processed_image = ResultImageData(
                    result_id=result.id, image=img_url
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
            return JSONResponse(
                {"error": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        return JSONResponse(
            {"error": error_message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
