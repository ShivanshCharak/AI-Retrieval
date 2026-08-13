from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import query, ingestion, auth
from app.api.v1.evaluation.classification import classification

api_router = APIRouter()

api_router.include_router(query.router, prefix="/v1", tags=["Query"])
api_router.include_router(ingestion.router, prefix="/v1", tags=["Ingestion"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
api_router.include_router(classification.router, prefix="/v1", tags=["EVALUATION"])
