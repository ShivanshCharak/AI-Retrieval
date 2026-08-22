from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.db.database import engine
from app.db.models import Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(api_router, prefix="/api")

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Welcome to fastapi"}


app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
