from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import database, schemas, models
from hashing import Hashing

router = APIRouter(prefix='/users', tags=['Users'])
get_db = database.get_db


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hashing the password
    hashed_password = Hashing.bcrypt(user.password)

    # Creating a new user using the User model
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        address=user.address,
        blood_group=user.blood_group,
        gender=user.gender,
        contact_no=user.contact_no,
        hashed_password=hashed_password
    )

    # Adding the new user to the database session
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Returning the newly created user
    return new_user


# get the user by id
@router.get("/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    return user
