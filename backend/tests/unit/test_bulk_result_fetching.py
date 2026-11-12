from unittest.mock import MagicMock

from app.services.bulk_service import BulkService


def get_valid_records():
    return [
        {
            "board": "dhaka",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "123456",
            "reg": "1234567890",
        },
        {
            "board": "rajshahi",
            "exam": "ssc",
            "year": "2025",
            "result_type": "1",
            "roll": "654321",
            "reg": "0987654321",
        },
    ]


def test_fetch_bulk_results_success():

    service = BulkService()

    service.result_service.get_individual_result = MagicMock(
        return_value={"gpa": "5.00"}
    )

    records = get_valid_records()

    results = service.fetch_bulk_results(records)

    assert len(results) == 2
    assert results[0]["processing_status"] == "Success"
    assert results[1]["processing_status"] == "Success"
    assert results[0]["result"] == {"gpa": "5.00"}


def test_fetch_bulk_results_partial_failure():

    service = BulkService()

    service.result_service.get_individual_result = MagicMock(
        side_effect=[
            {"gpa": "5.00"},
            Exception("Result retrieval failed"),
        ]
    )

    records = get_valid_records()

    results = service.fetch_bulk_results(records)

    assert len(results) == 2
    assert results[0]["processing_status"] == "Success"
    assert results[1]["processing_status"] == "Failed"
    assert results[1]["result"] is None
    assert results[1]["error"] == "Result retrieval failed"


def test_fetch_bulk_results_all_failed():

    service = BulkService()

    service.result_service.get_individual_result = MagicMock(
        side_effect=Exception("Service unavailable")
    )

    records = get_valid_records()

    results = service.fetch_bulk_results(records)

    assert len(results) == 2
    assert all(
        record["processing_status"] == "Failed"
        for record in results
    )


def test_fetch_bulk_results_empty():

    service = BulkService()

    results = service.fetch_bulk_results([])

    assert results == []