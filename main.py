from fastapi import FastAPI
from database import engine
from routers import user
import models as models

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
