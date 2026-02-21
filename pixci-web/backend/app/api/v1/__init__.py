"""API v1 routes"""
from fastapi import APIRouter
from app.api.v1 import health, encode, decode

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(encode.router, prefix="/encode", tags=["encode"])
api_router.include_router(decode.router, prefix="/decode", tags=["decode"])
