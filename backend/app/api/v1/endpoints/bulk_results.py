
from typing import Literal

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.services.bulk_service import BulkService
from app.integrations.eboardresults.exceptions import EBoardResponseError

router = APIRouter()

bulk_service = BulkService()


@router.post("/")
async def process_bulk_results(
    file: UploadFile = File(...),
    output_format: Literal["json", "csv", "excel"] = Query("json", alias="format"),
):
    try:
        records = bulk_service.read_file(file)

        result = bulk_service.process_bulk_records(records)

        # Return JSON response
        if output_format == "json":
            return {
                "success": True,
                "message": "Bulk file processed successfully.",
                "data": result,
            }

        # Generate CSV report
        if output_format == "csv":
            report = bulk_service.generate_csv_report(
                result["results"],
                result["invalid_data"],
            )

            return StreamingResponse(
                report,
                media_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="bulk_results.csv"'
                },
            )

        # Generate Excel report
        report = bulk_service.generate_excel_report(
            result["results"],
            result["invalid_data"],
        )

        return StreamingResponse(
            report,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="bulk_results.xlsx"'
            },
        )

    except EBoardResponseError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        await file.close()