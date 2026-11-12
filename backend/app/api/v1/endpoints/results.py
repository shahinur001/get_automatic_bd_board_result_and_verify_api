
from fastapi import APIRouter, HTTPException

from app.schemas.result import (
    StudentResultRequest,
    StudentResultResponse,
)
from app.services.result_service import ResultService
from app.integrations.eboardresults.exceptions import (
    EBoardResultsError,
    EBoardConnectionError,
    EBoardResponseError,
    EBoardAccessError,
)

router = APIRouter()

result_service = ResultService()


@router.post("/", response_model=StudentResultResponse)
async def get_result(student: StudentResultRequest):

    try:
        result = result_service.get_individual_result(
            request=student
        )

        return StudentResultResponse(
            success=True,
            message="Student result retrieved successfully.",
            data=result,
        )

    except EBoardConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except EBoardAccessError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except EBoardResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except EBoardResultsError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
