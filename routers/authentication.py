from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from hashing import Hashing
import database, models
from JWTtoken import get_current_user, create_refresh_token, create_access_token
from jose import JWTError, jwt
import os


router = APIRouter(tags=["Authentication"])


SECRET_KEY = os.getenv("JWTtoken")
REFRESH_SECRET_KEY = os.getenv("REFRESH_KEY")
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 30


# Login
@router.post("/login")
def login(
    authentication: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    # Check if the user exists
    user = (
        db.query(models.User)
        .filter(models.User.username == authentication.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid username"
        )
    # Check if the password is correct
    if not Hashing.verify(user.hashed_password, authentication.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Password"
        )
    # Check if the account is verified
    if user.is_verified != True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account Not Verified"
        )

    # Generate access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "is_admin": user.is_admin,
            "hospital_id": user.hospital_id,
            "is_hospital_admin": user.is_hospital_admin,
        }
    )

    # Generate refresh token
    refresh_token = create_refresh_token(
        data={
            "sub": user.username,
            "id": user.id,
        }
    )

    # Return both tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Route to refresh access token
@router.post("/refresh-token")
def refresh_token(refresh_token: str):
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        if username is None or id is None:
            raise get_user_exception()

        # Create a new access token
        new_access_token = create_access_token({"sub": username, "id": id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


# Home route for authenticated users
@router.get("/home")
async def home(current_user: models.User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.username}, you are successfully logged in!"
    }
