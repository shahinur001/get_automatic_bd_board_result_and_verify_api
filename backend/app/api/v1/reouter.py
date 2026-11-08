from fastapi import APIRouter

from app.api.v1.endpoints import (
    results,
    bulk_results,
    verification
)

api_router = APIRouter()

api_router.include_router(
    results.router,
    prefix="/results",
    tags=["Individual Results"]
)

api_router.include_router(
    bulk_results.router,
    prefix="/bulk-results",
    tags=["Bulk Results"]
)

api_router.include_router(
    verification.router,
    prefix="/verification",
    tags=["Student Verification"]
)