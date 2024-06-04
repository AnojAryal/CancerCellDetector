from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from database import engine
from routers import (
    user,
    authentication,
    password_reset,
    hospitals,
    patients,
    cell_tests,
)
import models as models
import cleanup
import os
import logging
from middleware.advanced import AdvancedMiddleWare

from middleware.hospital_access import HospitalAccessMiddleware


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

models.Base.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Add the custom middleware
rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", 1))


app.add_middleware(AdvancedMiddleWare, rate_limit=rate_limit_seconds)


# Add CORS middleware
origins = ["http://localhost", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(HospitalAccessMiddleware)

# Include routers
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(password_reset.router)
app.include_router(hospitals.router)
app.include_router(patients.router)
app.include_router(cell_tests.router)
