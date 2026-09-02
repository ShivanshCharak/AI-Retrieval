from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.db.database import engine
from app.db.models import Base
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

app.include_router(api_router, prefix="/api")


async def init_db():
    """Initialize database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Run DB initialization at startup
@app.on_event("startup")
async def startup():
    await init_db()


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
