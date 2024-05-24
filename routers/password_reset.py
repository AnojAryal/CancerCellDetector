from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import database, schemas, models
from email_utils import send_password_reset_email
import hashing
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/password-change", tags=["Password-reset"])

SECRET_KEY = "09d18e094faa6ca2646c818166b7a18103b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30

serializer = URLSafeTimedSerializer(SECRET_KEY)

@router.post("/send-reset-email")
async def send_reset_email(email: str, db: Session = Depends(database.get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            # Generate access token
            token = serializer.dumps(email, salt="password-reset-salt")
            # Send email with access token
            send_password_reset_email(email, token)
            return {"message": "Password reset email sent"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        db.close()

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(token: str = None, request: Request = None):
    if token is None:
        # If token is not provided, return an error response
        return HTMLResponse("Token not provided", status_code=400)

    try:
        email = serializer.loads(
            token, salt="password-reset-salt", max_age=TOKEN_EXPIRY_MINUTES * 60
        )
    except SignatureExpired:
        return HTMLResponse("Token expired", status_code=400)
    except BadSignature:
        return HTMLResponse("Invalid token", status_code=400)

    return templates.TemplateResponse(
        "reset-password.html", {"request": request, "token": token}
    )

@router.post("/reset-password/{token}")
async def reset_password(
    token: str, new_password: str = Form(...), db: Session = Depends(database.get_db)
):
    try:
        email = serializer.loads(
            token, salt="password-reset-salt", max_age=TOKEN_EXPIRY_MINUTES * 60
        )
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")

    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            hashed_password = hashing.Hashing.bcrypt(new_password)
            user.hashed_password = hashed_password
            db.commit()
            return {"message": "Password reset successful"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        db.close()
