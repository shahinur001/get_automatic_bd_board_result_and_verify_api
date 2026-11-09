from unittest.mock import patch, MagicMock
from app.services.result_service import ResultService
from app.schemas.result import StudentResultRequest
from app.core.config import settings

def test_get_individual_result_success():
    request = StudentResultRequest(
        board=settings.EXAM_BOARD,
        exam=settings.EXAM_TYPE,
        year=settings.EXAM_YEAR,
        result_type=1,
        roll=settings.ROLL,
        reg=settings.REG_NO,
    )

    expected_result = {
        "status": 0,
        "msg": "Success",
        "res": {},
    }

    with patch("app.services.result_service.EBoardResultsClient") as mock_client_class, \
         patch("app.services.result_service.CaptchaClient") as mock_captcha_class, \
         patch("app.services.result_service.Image.open") as mock_image_open, \
         patch("app.services.result_service.ExtractText") as mock_ocr_class, \
         patch("app.services.result_service.ResultParser") as mock_parser_class:

        # Mock instances
        mock_client = mock_client_class.return_value
        mock_captcha = mock_captcha_class.return_value
        mock_ocr = mock_ocr_class.return_value
        mock_parser = mock_parser_class.return_value

        # Set mock return values
        mock_captcha.get_captcha_image.return_value = b"fake_captcha_bytes"
        mock_ocr.get_extracted_text.return_value = "1234"
        mock_parser.get_ind_result.return_value = expected_result
        mock_image_instance = mock_image_open.return_value

        # Execute target method
        service = ResultService()
        result = service.get_individual_result(request=request)

        # Assert result matches expectation
        assert result == expected_result

        # Assert calls
        mock_client_class.assert_called_once()
        mock_client.get_page.assert_called_once()

        mock_captcha_class.assert_called_once_with(session=mock_client.session)
        mock_captcha.get_captcha_image.assert_called_once()

        mock_image_open.assert_called_once()
        mock_ocr_class.assert_called_once()
        mock_ocr.get_extracted_text.assert_called_once_with(img=mock_image_instance)

        mock_parser_class.assert_called_once_with(session=mock_client.session)
        mock_parser.get_ind_result.assert_called_once_with(
            exam_board=request.board,
            exam_type=request.exam,
            exam_year=request.year,
            result_type=request.result_type,
            roll=request.roll,
            registration=request.reg,
            extracted_text="1234",
        )

        # Verify session cleanup in finally block
        mock_client.session.close.assert_called_once()