from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from routers import user, authentication, password_reset, patient
import models as models
from starlette.staticfiles import StaticFiles
import cleanup


app = FastAPI()


models.Base.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


origins = ["http://localhost", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(password_reset.router)
app.include_router(patient.router)
