from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from hashing import Hashing
import database, schemas, models
from JWTtoken import get_current_user


router = APIRouter()
get_db = database.get_db


router = APIRouter(tags=["Password-change"])


@router.put("/change-password", response_model=schemas.PasswordChange)
async def change_password(
    password_change: schemas.PasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify current password
    if not Hashing.verify(
        current_user.hashed_password, password_change.current_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
        )

    # Hash the new password
    new_hashed_password = Hashing.bcrypt(password_change.new_password)

    current_user.hashed_password = new_hashed_password
    db.commit()

    return password_change
