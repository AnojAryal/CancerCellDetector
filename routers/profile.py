from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, models
from JWTtoken import get_current_user
from database import get_db

router = APIRouter(tags=["Profile"])


@router.get("/me", response_model=schemas.UserProfile)
async def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "address": current_user.address,
        "blood_group": current_user.blood_group,
        "gender": current_user.gender,
        "contact_no": current_user.contact_no,
    }


@router.patch("/me", response_model=schemas.UserProfile)
async def update_user_profile(
    user_update: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve the current user from the database
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        user.username = user_update.username
    if user_update.full_name:
        user.full_name = user_update.full_name
    if user_update.address:
        user.address = user_update.address
    if user_update.blood_group:
        user.blood_group = user_update.blood_group
    if user_update.gender:
        user.gender = user_update.gender
    if user_update.contact_no:
        user.contact_no = user_update.contact_no

    db.commit()
    db.refresh(user)

    return user
