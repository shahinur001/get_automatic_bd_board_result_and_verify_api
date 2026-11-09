from google import genai

from app.core.config import settings
from app.integrations.eboardresults.exceptions import EBoardResponseError

genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ExtractText:

    def get_extracted_text(self, img):
        try:
            ai_response = genai_client.models.generate_content(
                model='gemini-3.5-flash',
                contents=["Extract the text visible in this image precisely. Give only extracted number.", img]
        
            )

            if not ai_response.text:
                raise EBoardResponseError("Gemini returned no extracted text.")

            extracted_text = ai_response.text.strip()
            print(f"Extracted Text: {extracted_text}")
            
            return extracted_text

        except EBoardResponseError:
            raise

        except Exception as exc:
            raise EBoardResponseError(
                f"Gemini OCR failed: {exc}"
            ) from exc
