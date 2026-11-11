
from io import BytesIO
import pandas as pd

import pytest
from fastapi import UploadFile

from app.services.bulk_service import BulkService
from app.integrations.eboardresults.exceptions import EBoardResponseError


def create_upload_file(filename, content):
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
    )


def test_read_csv_success():

    csv_content = (
        b"board,exam,year,result_type,roll,reg\n"
        b"dhaka,ssc,2025,1,123456,789012\n"
        b"rajshahi,hsc,2024,1,234567,890123\n"
    )

    file = create_upload_file("students.csv", csv_content)

    service = BulkService()
    records = service.read_file(file)

    assert len(records) == 2
    assert records[0]["board"] == "dhaka"
    assert records[0]["roll"] == "123456"
    assert records[1]["exam"] == "hsc"


def test_read_unsupported_file():

    file = create_upload_file("students.pdf", b"dummy content")

    service = BulkService()

    with pytest.raises(EBoardResponseError):
        service.read_file(file)


def test_read_empty_csv():

    csv_content = b"board,exam,year,result_type,roll,reg\n"

    file = create_upload_file("students.csv", csv_content)

    service = BulkService()

    with pytest.raises(EBoardResponseError):
        service.read_file(file)


def test_read_csv_missing_columns():

    csv_content = (
        b"board,exam,roll\n"
        b"dhaka,ssc,123456\n"
    )

    file = create_upload_file("students.csv", csv_content)

    service = BulkService()

    with pytest.raises(EBoardResponseError):
        service.read_file(file)


def test_read_excel_success():

    dataframe = pd.DataFrame([
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "001234",
            "reg": "000789",
        },
        {
            "board": "rajshahi",
            "exam": "hsc",
            "year": "2024",
            "result_type": "1",
            "roll": "002345",
            "reg": "000890",
        },
    ])

    excel_buffer = BytesIO()
    dataframe.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    file = create_upload_file(
        "students.xlsx",
        excel_buffer.getvalue(),
    )

    service = BulkService()
    records = service.read_file(file)

    assert len(records) == 2
    assert records[0]["board"] == "dhaka"
    assert records[0]["roll"] == "001234"
    assert records[0]["reg"] == "000789"


def test_validate_records_success():

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "789012",
        }
    ]

    service = BulkService()
    valid_records, invalid_records = service.validate_records(records)

    assert len(valid_records) == 1
    assert len(invalid_records) == 0
    assert valid_records[0]["roll"] == "123456"


def test_validate_records_missing_roll():

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "",
            "reg": "789012",
        }
    ]

    service = BulkService()
    valid_records, invalid_records = service.validate_records(records)

    assert len(valid_records) == 0
    assert len(invalid_records) == 1
    assert "error" in invalid_records[0]


def test_validate_records_invalid_year():

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "123456",
            "reg": "789012",
        }
    ]

    service = BulkService()
    valid_records, invalid_records = service.validate_records(records)

    assert len(valid_records) == 0
    assert len(invalid_records) == 1
    assert "error" in invalid_records[0]


def test_validate_records_invalid_result_type():

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "5",
            "roll": "123456",
            "reg": "789012",
        }
    ]

    service = BulkService()
    valid_records, invalid_records = service.validate_records(records)

    assert len(valid_records) == 0
    assert len(invalid_records) == 1
    assert "error" in invalid_records[0]


def test_validate_mixed_records():

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "789012",
        },
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "123457",
            "reg": "789013",
        },
    ]

    service = BulkService()

    valid_records, invalid_records = service.validate_records(records)

    assert len(valid_records) == 1
    assert len(invalid_records) == 1

    assert valid_records[0]["roll"] == "123456"
    assert invalid_records[0]["roll"] == "123457"
    assert invalid_records[0]["row_number"] == 3
    assert "error" in invalid_records[0]


def test_generate_excel_report():
    service = BulkService()

    valid_records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "987654",
        }
    ]

    invalid_records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "123457",
            "reg": "987655",
            "error": "Invalid examination year.",
            "row_number": 3,
        }
    ]

    report = service.generate_excel_report(
        valid_records,
        invalid_records,
    )

    dataframe = pd.read_excel(report, dtype=str)

    assert len(dataframe) == 2
    assert dataframe.iloc[0]["processing_status"] == "Valid"
    assert dataframe.iloc[1]["processing_status"] == "Invalid"
    assert dataframe.iloc[1]["error"] == "Invalid examination year."


def test_generate_csv_report():
    service = BulkService()

    valid_records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "987654",
        }
    ]

    invalid_records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "123457",
            "reg": "987655",
            "error": "Invalid examination year.",
            "row_number": 3,
        }
    ]

    report = service.generate_csv_report(
        valid_records,
        invalid_records,
    )

    dataframe = pd.read_csv(report, dtype=str)

    assert len(dataframe) == 2
    assert dataframe.iloc[0]["processing_status"] == "Valid"
    assert dataframe.iloc[1]["processing_status"] == "Invalid"
    assert dataframe.iloc[1]["error"] == "Invalid examination year."



def test_process_bulk_records_all_valid():
    service = BulkService()

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "987654",
        },
        {
            "board": "rajshahi",
            "exam": "ssc",
            "year": "2025",
            "result_type": "2",
            "roll": "234567",
            "reg": "876543",
        },
    ]

    result = service.process_bulk_records(records)

    assert result["total_records"] == 2
    assert result["valid_records"] == 2
    assert result["invalid_records"] == 0
    assert len(result["valid_data"]) == 2
    assert len(result["invalid_data"]) == 0



def test_process_bulk_records_all_invalid():
    service = BulkService()

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "123456",
            "reg": "987654",
        },
        {
            "board": "rajshahi",
            "exam": "ssc",
            "year": "2025",
            "result_type": "5",
            "roll": "234567",
            "reg": "876543",
        },
    ]

    result = service.process_bulk_records(records)

    assert result["total_records"] == 2
    assert result["valid_records"] == 0
    assert result["invalid_records"] == 2
    assert len(result["valid_data"]) == 0
    assert len(result["invalid_data"]) == 2



def test_process_bulk_records_mixed():
    service = BulkService()

    records = [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "987654",
        },
        {
            "board": "rajshahi",
            "exam": "ssc",
            "year": "invalid",
            "result_type": "1",
            "roll": "234567",
            "reg": "876543",
        },
    ]

    result = service.process_bulk_records(records)

    assert result["total_records"] == 2
    assert result["valid_records"] == 1
    assert result["invalid_records"] == 1
    assert result["valid_data"][0]["roll"] == "123456"
    assert result["invalid_data"][0]["roll"] == "234567"



