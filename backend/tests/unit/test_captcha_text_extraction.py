
from pathlib import Path
import requests
import time
from io import BytesIO
from PIL import Image

from app.integrations.eboardresults.captcha import CaptchaClient
from app.integrations.eboardresults.client import EBoardResultsClient
from app.integrations.eboardresults.exceptions import EBoardResultsError
from app.integrations.gemini.ocr import ExtractText

client = EBoardResultsClient()


try:
    # Use an existing authorized session.
    response = client.get_page()

    for i in range(5):
    
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

except EBoardResultsError as error:
    print("Integration error:", error)

finally:
    client.session.close()
