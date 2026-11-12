
# from fastapi.testclient import TestClient

# from app.main import app

# client = TestClient(app)


# def get_csv_file():
#     csv_content = (
#         "board,exam,year,result_type,roll,reg\n"
#         "DHAKA,SSC,2025,1,123456,1234567890\n"
#         "RAJSHAHI,HSC,2024,1,654321,9876543210\n"
#     )

#     return {
#         "file": (
#             "students.csv",
#             csv_content.encode("utf-8"),
#             "text/csv",
#         )
#     }


# def test_bulk_results_json_success():

#     response = client.post(
#         "/api/v1/bulk-results/?format=json",
#         files=get_csv_file(),
#     )

#     assert response.status_code == 200

#     data = response.json()

#     assert data["success"] is True
#     assert data["data"]["total_records"] == 2
#     assert data["data"]["valid_records"] == 2
#     assert data["data"]["invalid_records"] == 0


# def test_bulk_results_csv_success():

#     response = client.post(
#         "/api/v1/bulk-results/?format=csv",
#         files=get_csv_file(),
#     )

#     assert response.status_code == 200
#     assert "text/csv" in response.headers["content-type"]
#     assert "attachment" in response.headers["content-disposition"]

#     content = response.content.decode("utf-8-sig")

#     assert "processing_status" in content
#     assert "Valid" in content
#     assert "123456" in content


# def test_bulk_results_excel_success():

#     response = client.post(
#         "/api/v1/bulk-results/?format=excel",
#         files=get_csv_file(),
#     )

#     assert response.status_code == 200

#     assert (
#         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         in response.headers["content-type"]
#     )

#     assert response.content.startswith(b"PK")
#     assert "attachment" in response.headers["content-disposition"]


# def test_bulk_results_unsupported_file():

#     response = client.post(
#         "/api/v1/bulk-results/?format=json",
#         files={
#             "file": (
#                 "students.txt",
#                 b"Some test content",
#                 "text/plain",
#             )
#         },
#     )

#     assert response.status_code == 400
#     assert "Only CSV and XLSX files are supported" in response.json()["detail"]


# def test_bulk_results_missing_columns():

#     csv_content = (
#         "board,exam,year,roll\n"
#         "DHAKA,SSC,2025,123456\n"
#     )

#     response = client.post(
#         "/api/v1/bulk-results/?format=json",
#         files={
#             "file": (
#                 "students.csv",
#                 csv_content.encode("utf-8"),
#                 "text/csv",
#             )
#         },
#     )

#     assert response.status_code == 400
#     assert "Missing required columns" in response.json()["detail"]





from io import BytesIO
from unittest.mock import MagicMock

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.bulk_results import bulk_service

client = TestClient(app)


def get_csv_file():
    csv_content = (
        "board,exam,year,result_type,roll,reg\n"
        "DHAKA,SSC,2025,1,123456,1234567890\n"
        "RAJSHAHI,HSC,2024,1,654321,9876543210\n"
        "DHAKA,SSC,invalid,1,111111,1111111111\n"
    )

    return {
        "file": (
            "students.csv",
            csv_content.encode("utf-8"),
            "text/csv",
        )
    }


def get_mock_bulk_result():
    return {
        "total_records": 3,
        "valid_records": 2,
        "invalid_records": 1,
        "successful_results": 1,
        "failed_results": 1,
        "valid_data": [
            {
                "board": "DHAKA",
                "exam": "SSC",
                "year": "2025",
                "result_type": "1",
                "roll": "123456",
                "reg": "1234567890",
            },
            {
                "board": "RAJSHAHI",
                "exam": "HSC",
                "year": "2024",
                "result_type": "1",
                "roll": "654321",
                "reg": "9876543210",
            },
        ],
        "results": [
            {
                "board": "DHAKA",
                "exam": "SSC",
                "year": "2025",
                "result_type": "1",
                "roll": "123456",
                "reg": "1234567890",
                "processing_status": "Success",
                "result": {
                    "success": True,
                    "data": {
                        "res": {
                            "name": "DEMO STUDENT",
                            "fname": "DEMO FATHER",
                            "mname": "DEMO MOTHER",
                            "roll_no": "123456",
                            "regno": "1234567890",
                            "res_detail": "GPA=5.00",
                            "display_details": "101:A+",
                        },
                        "sub_details": [
                            {
                                "SUB_CODE": "101",
                                "SUB_NAME": "DEMO SUBJECT",
                            }
                        ],
                    },
                },
                "error": "",
            },
            {
                "board": "RAJSHAHI",
                "exam": "HSC",
                "year": "2024",
                "result_type": "1",
                "roll": "654321",
                "reg": "9876543210",
                "processing_status": "Failed",
                "result": None,
                "error": "Demo result retrieval failed.",
            },
        ],
        "invalid_data": [
            {
                "board": "DHAKA",
                "exam": "SSC",
                "year": "invalid",
                "result_type": "1",
                "roll": "111111",
                "reg": "1111111111",
                "error": "Invalid examination year.",
                "row_number": 4,
            }
        ],
    }


def mock_bulk_processing(monkeypatch):
    mock = MagicMock(return_value=get_mock_bulk_result())

    monkeypatch.setattr(
        bulk_service,
        "process_bulk_records",
        mock,
    )

    return mock


def test_bulk_results_json_success(monkeypatch):

    mock = mock_bulk_processing(monkeypatch)

    response = client.post(
        "/api/v1/bulk-results/?format=json",
        files=get_csv_file(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["total_records"] == 3
    assert data["data"]["valid_records"] == 2
    assert data["data"]["invalid_records"] == 1

    assert data["data"]["successful_results"] == 1
    assert data["data"]["failed_results"] == 1

    assert len(data["data"]["results"]) == 2
    assert data["data"]["results"][0]["processing_status"] == "Success"
    assert data["data"]["results"][1]["processing_status"] == "Failed"

    assert data["data"]["results"][0]["result"]["data"]["res"]["name"] == "DEMO STUDENT"

    assert len(data["data"]["invalid_data"]) == 1

    mock.assert_called_once()


def test_bulk_results_csv_success(monkeypatch):

    mock_bulk_processing(monkeypatch)

    response = client.post(
        "/api/v1/bulk-results/?format=csv",
        files=get_csv_file(),
    )

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]

    dataframe = pd.read_csv(
        BytesIO(response.content),
        dtype=str,
    )

    assert len(dataframe) == 3

    # Successful result
    assert dataframe.iloc[0]["processing_status"] == "Success"
    assert dataframe.iloc[0]["student_name"] == "DEMO STUDENT"
    assert dataframe.iloc[0]["gpa"] == "5.00"

    # Failed result
    assert dataframe.iloc[1]["processing_status"] == "Failed"
    assert dataframe.iloc[1]["error"] == "Demo result retrieval failed."

    # Invalid input
    assert dataframe.iloc[2]["processing_status"] == "Invalid"
    assert dataframe.iloc[2]["error"] == "Invalid examination year."


def test_bulk_results_excel_success(monkeypatch):

    mock_bulk_processing(monkeypatch)

    response = client.post(
        "/api/v1/bulk-results/?format=excel",
        files=get_csv_file(),
    )

    assert response.status_code == 200

    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in response.headers["content-type"]
    )

    assert response.content.startswith(b"PK")
    assert "attachment" in response.headers["content-disposition"]

    dataframe = pd.read_excel(
        BytesIO(response.content),
        dtype=str,
    )

    assert len(dataframe) == 3

    assert dataframe.iloc[0]["processing_status"] == "Success"
    assert dataframe.iloc[0]["student_name"] == "DEMO STUDENT"

    assert dataframe.iloc[1]["processing_status"] == "Failed"
    assert dataframe.iloc[2]["processing_status"] == "Invalid"


def test_bulk_results_unsupported_file():

    response = client.post(
        "/api/v1/bulk-results/?format=json",
        files={
            "file": (
                "students.txt",
                b"Some test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only CSV and XLSX files are supported" in response.json()["detail"]


def test_bulk_results_missing_columns():

    csv_content = (
        "board,exam,year,roll\n"
        "DHAKA,SSC,2025,123456\n"
    )

    response = client.post(
        "/api/v1/bulk-results/?format=json",
        files={
            "file": (
                "students.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]
