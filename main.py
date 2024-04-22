from fastapi import FastAPI
from database import engine
from routers import user, authentication
import models as models


app = FastAPI()

# Create database tables if they don't exist
models.Base.metadata.create_all(engine)

app.include_router(user.router)
app.include_router(authentication.router)