from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.reouter import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API for Bangladesh Education Board Result Retrieval and Verification."
)


@app.get("/")
async def root():
    return {
        "message": "BD Board Result API is running!",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }

app.include_router(api_router, prefix="/api/v1")