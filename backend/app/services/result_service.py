import time
from io import BytesIO
from PIL import Image

from app.integrations.eboardresults.client import EBoardResultsClient
from app.integrations.eboardresults.result_parser import ResultParser
from app.integrations.eboardresults.captcha import CaptchaClient
from app.integrations.gemini.ocr import ExtractText
from app.schemas.result import StudentResultRequest

class ResultService:

    def get_individual_result(
            self,
            request: StudentResultRequest,
    ) -> dict:
        client = EBoardResultsClient()

        try:
            client.get_page()

            captcha_client = CaptchaClient(session=client.session)

            image_data = captcha_client.get_captcha_image(
                timestamp=str(int(time.time() * 1000))
            )

            img = Image.open(BytesIO(image_data))

            ocr_client = ExtractText()
            output_extracted_text = ocr_client.get_extracted_text(img=img)

            result_client = ResultParser(session=client.session)

            result = result_client.get_ind_result(
                exam_board=request.board,
                exam_type=request.exam,
                exam_year=request.year,
                result_type=request.result_type,
                roll=request.roll,
                registration=request.reg,
                extracted_text=output_extracted_text,
            )

            return result

        finally:
            client.session.close()