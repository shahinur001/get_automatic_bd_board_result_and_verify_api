import requests

from app.core.config import settings
from app.integrations.gemini.ocr import ExtractText
from app.integrations.eboardresults.exceptions import (
    EBoardResponseError,
    EBoardConnectionError,
    EBoardResultsError,
    EBoardAccessError
)

class ResultParser:
    def __init__(self, session: requests.Session):
        self.session = session
        self.base_url = settings.EBR_BASE_URL.rstrip("/")

    def get_ind_result(
            self, 
            exam_board: str, 
            exam_type: str, 
            exam_year: str, 
            result_type: int, 
            roll: str, 
            registration: str,
            extracted_text: str
            ):

        url = f"{self.base_url}/v2/getres"
        print(url)

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": settings.EBR_REFERER
        }

        try:
            response = self.session.post(
                url,
                params={
                    "board": exam_board,
                    "exam": exam_type,
                    "year": exam_year,
                    "result_type": result_type,
                    "roll": roll,
                    "reg": registration,
                    "eiin": "",
                    "dcode": "",
                    "ccode": "",
                    "captcha": extracted_text
                },
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

             # Parse JSON
            try:
                payload = response.json()
            except ValueError as exc:
                raise EBoardResponseError(
                    "External service returned invalid JSON."
                ) from exc

            
            if payload.get("status") != 0 and payload.get("msg") != "Success":
                raise EBoardResponseError(
                    "Result not get successfully. "
                    f"Error Message: {payload.get('msg', 'Unknown error')}"
                )
            

            return payload

        except requests.Timeout as exc:
            raise EBoardConnectionError(
                "Result request time out."
            ) from exc

        except requests.ConnectionError as exc:
            raise EBoardConnectionError(
                "Could not connect to RESULT service."
            ) from exc

        except requests.HTTPError as exc:
            raise EBoardResponseError(
                f"RESULT request failed: HTTP {response.status_code}"
            ) from exc