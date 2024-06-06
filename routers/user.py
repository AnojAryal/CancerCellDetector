from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import database, schemas, models
from hashing import Hashing
from email_utils import send_verification_email
from JWTtoken import get_current_user, get_admin_or_hospital_admin
from typing import List

import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/users", tags=["Users"])
get_db = database.get_db

SECRET_KEY = os.getenv("UserSecretKey")
ALGORITHM = "HS256"


# create a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_hospital_admin),
):
    # Checking if the username or email already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Set is_admin to False by default if the current user is not an admin
    is_admin = user.is_admin if current_user.is_admin else False

    print("is_admin after setting in endpoint:", is_admin)

    # Determine hospital_id based on the current user's role
    hospital_id = (
        user.hospital_id if current_user.is_admin else current_user.hospital_id
    )

    hashed_password = Hashing.bcrypt(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        address=user.address,
        blood_group=user.blood_group,
        gender=user.gender,
        contact_no=user.contact_no,
        hashed_password=hashed_password,
        is_verified=False,
        is_admin=is_admin,
        is_hospital_admin=user.is_hospital_admin,
        hospital_id=hospital_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate a verification token
    expire = datetime.utcnow() + timedelta(hours=24)
    verification_token = jwt.encode(
        {"user_id": str(new_user.id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM
    )

    # Schedule the send_verification_email task to run in the background
    background_tasks.add_task(
        send_verification_email, new_user.email, verification_token
    )

    return {
        "message": "User created. Please check your email for verification instructions."
    }


# get all user
@router.get("/", response_model=List[schemas.User])
async def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_hospital_admin),
):
    if current_user.is_admin:
        users = db.query(models.User).all()
    elif current_user.is_hospital_admin:
        users = (
            db.query(models.User)
            .filter(models.User.hospital_id == current_user.hospital_id)
            .all()
        )
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return users


# Retrieve the user by ID
@router.get("/{user_id}", response_model=schemas.User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    # admin, access to all users details
    if current_user.is_admin:
        return user

    # hospital admin, access only to users of their hospital
    if current_user.is_hospital_admin:
        if current_user.hospital_id != user.hospital_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this user's details",
            )
        return user

    # ordinary user, access only to their own details
    if current_user.id == user_id:
        return user

    # If none of the above conditions are met, raise a permission error
    raise HTTPException(
        status_code=403,
        detail="You do not have permission",
    )


# update users by id
@router.patch("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_hospital_admin),
):
    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admins or the hospital admin can update a user
    if not (
        current_user.is_admin
        or (
            current_user.is_hospital_admin
            and current_user.hospital_id == user_to_update.hospital_id
        )
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update the fields that are allowed to be updated
    if user.username is not None:
        user_to_update.username = user.username
    if user.full_name is not None:
        user_to_update.full_name = user.full_name
    if user.address is not None:
        user_to_update.address = user.address
    if user.blood_group is not None:
        user_to_update.blood_group = user.blood_group
    if user.gender is not None:
        user_to_update.gender = user.gender
    if user.contact_no is not None:
        user_to_update.contact_no = user.contact_no

    # Admin-specific updates
    if current_user.is_admin:
        if user.is_hospital_admin is not None:
            # Allow admin to change hospital admin status
            user_to_update.is_hospital_admin = user.is_hospital_admin

        if user.is_admin is not None:
            # Ensure admin cannot demote themselves
            if user.is_admin:
                user_to_update.is_admin = user.is_admin

        if user.hospital_id is not None:
            # Check and update hospital ID if provided
            hospital_exists = (
                db.query(models.Hospital)
                .filter(models.Hospital.id == user.hospital_id)
                .first()
            )
            if not hospital_exists:
                raise HTTPException(status_code=404, detail="Hospital not found")
                user_to_update.hospital_id = user.hospital_id

    # Hospital admin-specific updates
    elif current_user.is_hospital_admin:
        # Hospital admins cannot change the hospital ID
        if (
            user.hospital_id is not None
            and user.hospital_id != current_user.hospital_id
        ):
            raise HTTPException(
                status_code=403, detail="Hospital admins cannot change the hospital ID"
            )

        if user.is_hospital_admin is not None:
            # Allow hospital admin to change their own status
            user_to_update.is_hospital_admin = user.is_hospital_admin

        if user.is_admin is not None:
            # Ensure hospital admin cannot promote themselves
            if not user.is_admin:
                user_to_update.is_admin = user.is_admin

    db.commit()
    db.refresh(user_to_update)

    return user_to_update


# delete user by id
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_hospital_admin),
):
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admins or the hospital admin can delete a user
    if not (
        current_user.is_admin
        or (
            current_user.is_hospital_admin
            and current_user.hospital_id == user_to_delete.hospital_id
        )
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(user_to_delete)
    db.commit()

    return {"message": "User deleted successfully"}


# verify users email
@router.get("/verify/{token}", response_model=dict)
def verify_user_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            return {"message": "Email is already verified"}

        user.is_verified = True
        db.commit()

        return {"message": "Email verified successfully"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
