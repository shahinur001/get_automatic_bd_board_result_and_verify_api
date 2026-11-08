from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def verify_student():
    return {
        "message": "Student verification endpoint is working! This will complete in future."
    }
