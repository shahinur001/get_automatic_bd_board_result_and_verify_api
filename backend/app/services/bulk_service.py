from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from app.integrations.eboardresults.exceptions import EBoardResponseError
from app.schemas.result import StudentResultRequest
from app.services.result_service import ResultService

class BulkService:

    def __init__(self):
        self.result_service = ResultService()

    REQUIRED_COLUMNS = {
        "board",
        "exam",
        "year",
        "result_type",
        "roll",
        "reg",
    }

    ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

    def read_file(self, file: UploadFile) -> list[dict]:

        extension = Path(file.filename or "").suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise EBoardResponseError(
                "Only CSV and XLSX files are supported"
            )

        try:
            if extension == ".csv":
                dataframe = pd.read_csv(
                    file.file,
                    dtype=str,
                    keep_default_na=False,
                )
            else:
                dataframe = pd.read_excel(
                    file.file,
                    dtype=str,
                    keep_default_na=False,
                )
        except Exception as exc:
            raise EBoardResponseError(
                "Could not read the uploaded file."
            ) from exc

        if dataframe.empty:
            raise EBoardResponseError(
                "The uploaded file contains no student records."
            )

        missing_columns = self.REQUIRED_COLUMNS - set(dataframe.columns)

        if missing_columns:
            raise EBoardResponseError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        dataframe = dataframe.fillna("")

        records = dataframe.to_dict(orient="records")

        return records

    
    def validate_records(self, records: list[dict]) -> tuple[list[dict], list[dict]]:

        valid_records = []
        invalid_records = []

        for index, record in enumerate(records, start=2):

            record = record.copy()

            required_fields = self.REQUIRED_COLUMNS

            missing_fields = [
                field for field in required_fields
                if not str(record.get(field, "")).strip()
            ]

            if missing_fields:
                record["error"] = (
                    f"Missing fields: {', '.join(missing_fields)}"
                )
                record["row_number"] = index
                invalid_records.append(record)
                continue

            if not str(record["year"]).strip().isdigit():
                record["error"] = "Invalid examination year."
                record["row_number"] = index
                invalid_records.append(record)
                continue

            if str(record["result_type"]).strip() not in {"1", "2"}:
                record["error"] = "Invalid result type."
                record["row_number"] = index
                invalid_records.append(record)
                continue

            valid_records.append(record)

        return valid_records, invalid_records


    def prepare_report_records(
        self,
        valid_records: list[dict],
        invalid_records: list[dict],
    ) -> list[dict]:

        report_records = []

        # Process valid records and retrieved results.
        for record in valid_records:

            report_record = {
                key: value
                for key, value in record.items()
                if key != "result"
            }

            result = record.get("result") or {}

            # Support both raw parser responses and wrapped API responses.
            result_data = result.get("data", result)

            student_data = result_data.get("res") or {}

            subject_details = result_data.get("sub_details") or []

            subject_names = {
                subject.get("SUB_CODE"): subject.get("SUB_NAME")
                for subject in subject_details
            }

            display_details = student_data.get("display_details", "")

            subject_grades = []

            for item in display_details.split(","):
                if ":" not in item:
                    continue

                code, grade = item.split(":", 1)

                subject_name = subject_names.get(code, code)

                subject_grades.append(
                    f"{subject_name}: {grade}"
                )

            result_summary = student_data.get("res_detail", "")

            gpa = (
                result_summary.split("=", 1)[1]
                if "=" in result_summary
                else ""
            )

            report_record.update({
                "processing_status": record.get(
                    "processing_status", "Valid"
                ),
                "student_name": student_data.get("name", ""),
                "father_name": student_data.get("fname", ""),
                "mother_name": student_data.get("mname", ""),
                "roll_no": student_data.get("roll_no", ""),
                "registration_no": student_data.get("regno", ""),
                "session": student_data.get("session", ""),
                "board_name": student_data.get("board_name", ""),
                "group": student_data.get("stud_group", ""),
                "student_type": student_data.get("stud_type", ""),
                "gender": student_data.get("sex", ""),
                "date_of_birth": student_data.get("dob", ""),
                "gpa": gpa,
                "institution": student_data.get("inst_name", ""),
                "thana": student_data.get("t_name", ""),
                "district": student_data.get("z_name", ""),
                "subject_grades": "; ".join(subject_grades),
                "error": record.get("error", ""),
            })

            report_records.append(report_record)

        # Process invalid records.
        for record in invalid_records:

            report_record = record.copy()
            report_record["processing_status"] = "Invalid"

            report_records.append(report_record)

        return report_records


    def generate_excel_report(
        self,
        valid_records: list[dict],
        invalid_records: list[dict],
    ) -> BytesIO:

        report_records = self.prepare_report_records(
            valid_records,
            invalid_records,
        )

        dataframe = pd.DataFrame(report_records)

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            dataframe.to_excel(
                writer,
                index=False,
                sheet_name="Bulk Results",
            )

        output.seek(0)

        return output

    
    def generate_csv_report(
        self,
        valid_records: list[dict],
        invalid_records: list[dict],
    ) -> BytesIO:

        report_records = self.prepare_report_records(
            valid_records,
            invalid_records,
        )

        dataframe = pd.DataFrame(report_records)

        output = BytesIO()

        dataframe.to_csv(
            output,
            index=False,
            encoding="utf-8-sig",
        )

        output.seek(0)

        return output


    def process_bulk_records(self, records: list[dict]) -> dict:

        valid_records, invalid_records = self.validate_records(records)

        fetched_results = self.fetch_bulk_results(valid_records)

        successful_records = [
            record for record in fetched_results
            if record["processing_status"] == "Success"
        ]

        failed_records = [
            record for record in fetched_results
            if record["processing_status"] == "Failed"
        ]

        return {
            "total_records": len(records),
            "valid_records": len(valid_records),
            "invalid_records": len(invalid_records),
            "successful_results": len(successful_records),
            "failed_results": len(failed_records),
            "valid_data": valid_records,
            "results": fetched_results,
            "invalid_data": invalid_records,
        }

    def fetch_bulk_results(
            self,
            valid_records: list[dict],
    ) -> list[dict]:

        results = []

        for record in valid_records:

            try:
                request = StudentResultRequest(
                    board=record["board"],
                    exam=record["exam"],
                    year=record["year"],
                    result_type=int(record["result_type"]),
                    roll=record["roll"],
                    reg=record["reg"],
                    eiin=record.get("eiin") or None,
                    dcode=record.get("dcode") or None,
                    ccode=record.get("ccode") or None,
                )

                result = self.result_service.get_individual_result(
                    request=request
                )

                results.append({
                    **record,
                    "processing_status": "Success",
                    "result": result,
                    "error": "",
                })

            except Exception as exc:

                results.append({
                    **record,
                    "processing_status": "Failed",
                    "result": None,
                    "error": str(exc),
                })

        return results

