
from pathlib import Path
import requests
import time

from app.integrations.eboardresults.captcha import CaptchaClient
from app.integrations.eboardresults.client import EBoardResultsClient
from app.integrations.eboardresults.exceptions import EBoardResultsError

client = EBoardResultsClient()


# session = requests.Session()

try:
    # Use an existing authorized session.
    response = client.get_page()
    captcha_client = CaptchaClient(client.session)

    image_data = captcha_client.get_captcha_image(
        timestamp=str(int(time.time() * 1000))
    )

    output_path = Path("captcha.png")
    output_path.write_bytes(image_data)

    print("CAPTCHA image received successfully!")
    print("Saved:", output_path.resolve())
    print("Image size:", len(image_data), "bytes")

except EBoardResultsError as error:
    print("Integration error:", error)

finally:
    client.session.close()
