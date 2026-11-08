from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def process_bulk_results():
    return {
        "message": "Bulk result endpoint is working!"
    }