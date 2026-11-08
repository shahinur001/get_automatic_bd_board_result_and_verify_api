from fastapi import APIRouter
from app.schemas.result import (
    StudentResultRequest,
    StudentResultResponse
)

router = APIRouter()

@router.post("/", response_model=StudentResultResponse)
async def get_result(student: StudentResultRequest):
    return StudentResultResponse(
        success=True,
        message="Student result request received successfully.",
        data=None
    )