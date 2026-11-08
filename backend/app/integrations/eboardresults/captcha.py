import requests

from app.core.config import settings
from app.integrations.eboardresults.exceptions import (
    EBoardConnectionError,
    EBoardResponseError
)

class CaptchaClient:

    def __init__(self, session: requests.Session):
        self.session = session
        self.base_url = settings.EBR_BASE_URL.rstrip("/")

    def get_captcha_image(self, timestamp: str) -> bytes:

        url = f"{self.base_url}/v2/captcha"
        print(url)

        headers = {
            "Accept": "image/*,*/*;q=0.8",
            "Referer": settings.EBR_REFERER,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        try:
            response = self.session.get(
                url,
                params={"t": timestamp},
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            # print("Requested URL:", response.url)
            # print("Status:", response.status_code)
            # print("Content-Type:", response.headers.get("Content-Type"))
            # print("Response Length:", len(response.content))
            # print("Response Preview:", response.text[:500])
            # print("Cookies:", self.session.cookies.get_dict())

            if not content_type.startswith("image/"):
                raise EBoardResponseError(
                    "Expect an image response, "
                    f"received {content_type}"
                )
            if not response.content:
                raise EBoardResponseError(
                    "Received and empty CAPTCHA image."
                )

            return response.content

        except requests.Timeout as exc:
            raise EBoardConnectionError(
                "CAPTCHA request timed out."
            ) from exc

        except requests.ConnectionError as exc:
            raise EBoardConnectionError(
                "Could not connect to CAPTCHA service."
            ) from exc

        except requests.HTTPError as exc:
            raise EBoardResponseError(
                f"CAPTCHA request failed: HTTP {response.status_code}"
            ) from exc