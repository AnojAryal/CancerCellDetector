from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import database, schemas, models
from hashing import Hashing
from email_utils import send_verification_email


router = APIRouter(prefix="/users", tags=["Users"])
get_db = database.get_db

SECRET_KEY = "f04b3e8a9d2c6e1b8a6c4e9b7d3f9a1c2e3b4d6f8a0c2e5b9d0a7f3b5d8f9a0c"
ALGORITHM = "HS256"


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
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


@router.get("/verify", response_model=dict)
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


# get the user by id
@router.get("/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    return user
