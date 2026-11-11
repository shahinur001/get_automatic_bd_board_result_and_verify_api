from pathlib import Path
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from app.integrations.eboardresults.exceptions import EBoardResponseError

class BulkService:

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

    def generate_excel_report(
            self,
            valid_records: list[dict],
            invalid_records: list[dict],
    ) -> BytesIO:

        report_records = []

        # Add successful records.
        for record in valid_records:
            report_record = record.copy()
            report_record["processing_status"] = "Valid"
            report_record["error"] = ""
            report_records.append(report_record)

        # Add invalid records.
        for record in invalid_records:
            report_record = record.copy()
            report_record["processing_status"] = "Invalid"
            report_records.append(report_record)

        dataframe = pd.DataFrame(report_records)

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            dataframe.to_excel(
                writer,
                index=False,
                sheet_name="Bulk Report",
            )

        output.seek(0)

        return output

    
    def generate_csv_report(
        self,
        valid_records: list[dict],
        invalid_records: list[dict],
    ) -> BytesIO:

        report_records = []

        # Add successful records.
        for record in valid_records:
            report_record = record.copy()
            report_record["processing_status"] = "Valid"
            report_record["error"] = ""
            report_records.append(report_record)

        # Add invalid records.
        for record in invalid_records:
            report_record = record.copy()
            report_record["processing_status"] = "Invalid"
            report_records.append(report_record)

        dataframe = pd.DataFrame(report_records)

        output = BytesIO()
        dataframe.to_csv(output, index=False, encoding="utf-8-sig")

        output.seek(0)

        return output


    def process_bulk_records(self, records: list[dict]) -> dict:

        valid_records, invalid_records = self.validate_records(records)

        return {
            "total_records": len(records),
            "valid_records": len(valid_records),
            "invalid_records": len(invalid_records),
            "valid_data": valid_records,
            "invalid_data": invalid_records,
        }

