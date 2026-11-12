
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.results import result_service
from app.integrations.eboardresults.exceptions import (
    EBoardResultsError,
    EBoardConnectionError,
    EBoardResponseError,
    EBoardAccessError,
)

client = TestClient(app)


@pytest.fixture
def valid_student_request():
    return {
        "board": "DHAKA",
        "exam": "SSC",
        "year": "2025",
        "result_type": 1,
        "roll": "123456",
        "reg": "1234567890",
    }


def test_get_result_success(monkeypatch, valid_student_request):

    expected_result = {
        "student_name": "Test Student",
        "roll": "123456",
        "gpa": "5.00",
    }

    def mock_get_result(request):
        return expected_result

    monkeypatch.setattr(
        result_service,
        "get_individual_result",
        mock_get_result,
    )

    response = client.post(
        "/api/v1/results/",
        json=valid_student_request,
    )
    print(response)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"] == expected_result


def test_get_result_connection_error(monkeypatch, valid_student_request):

    def mock_get_result(request):
        raise EBoardConnectionError("Connection failed")

    monkeypatch.setattr(
        result_service,
        "get_individual_result",
        mock_get_result,
    )

    response = client.post(
        "/api/v1/results/",
        json=valid_student_request,
    )

    assert response.status_code == 503


def test_get_result_access_error(monkeypatch, valid_student_request):

    def mock_get_result(request):
        raise EBoardAccessError("Access denied")

    monkeypatch.setattr(
        result_service,
        "get_individual_result",
        mock_get_result,
    )

    response = client.post(
        "/api/v1/results/",
        json=valid_student_request,
    )

    assert response.status_code == 403


def test_get_result_response_error(monkeypatch, valid_student_request):

    def mock_get_result(request):
        raise EBoardResponseError("Invalid response")

    monkeypatch.setattr(
        result_service,
        "get_individual_result",
        mock_get_result,
    )

    response = client.post(
        "/api/v1/results/",
        json=valid_student_request,
    )

    assert response.status_code == 502


def test_get_result_general_error(monkeypatch, valid_student_request):

    def mock_get_result(request):
        raise EBoardResultsError("Something went wrong")

    monkeypatch.setattr(
        result_service,
        "get_individual_result",
        mock_get_result,
    )

    response = client.post(
        "/api/v1/results/",
        json=valid_student_request,
    )

    assert response.status_code == 500
