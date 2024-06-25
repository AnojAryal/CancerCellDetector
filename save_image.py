from fastapi import (
    UploadFile,
    Path,
)
import uuid


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
