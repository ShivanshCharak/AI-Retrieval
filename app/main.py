from fastapi import FastAPI
from app.api.router import api_router
from app.db.database import engine
from app.db.models import Base

app = FastAPI()

app.include_router(api_router, prefix="/api")

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Welcome to fastapi"}
