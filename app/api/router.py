from fastapi import APIRouter
from app.api.v1 import query, ingestion, auth

api_router = APIRouter()

api_router.include_router(query.router, prefix="/v1", tags=["Query"])
api_router.include_router(ingestion.router, prefix="/v1", tags=["Ingestion"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
