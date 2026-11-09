
from pathlib import Path
import time
from io import BytesIO
from PIL import Image

from app.integrations.eboardresults.captcha import CaptchaClient
from app.integrations.eboardresults.client import EBoardResultsClient
from app.integrations.eboardresults.exceptions import EBoardResultsError
from app.integrations.gemini.ocr import ExtractText
from app.integrations.eboardresults.result_parser import ResultParser
from app.core.config import settings

client = EBoardResultsClient()


try:
    # Use an existing authorized session.
    response = client.get_page()

    for i in range(2):
    
        captcha_client = CaptchaClient(client.session)

        image_data = captcha_client.get_captcha_image(
            timestamp=str(int(time.time() * 1000))
        )

        output_path = Path("captcha.png")
        output_path.write_bytes(image_data)

        print("CAPTCHA image received successfully!")
        print("Saved:", output_path.resolve())
        print("Image size:", len(image_data), "bytes")

        img = Image.open(BytesIO(image_data))

        ocr_client = ExtractText()
        output_text = ocr_client.get_extracted_text(img=img)

        print(f"Test output: {output_text}")

        result_client = ResultParser(client.session)

        ind_result = result_client.get_ind_result(
            exam_board=settings.EXAM_BOARD,
            exam_type=settings.EXAM_TYPE,
            exam_year=settings.EXAM_YEAR,
            result_type=1,
            roll=settings.ROLL,
            registration=settings.REG_NO,
            extracted_text=str(output_text)
        )

        print("Result get succesfully")
        print(ind_result)

except EBoardResultsError as error:
    print("Integration error:", error)

finally:
    client.session.close()
