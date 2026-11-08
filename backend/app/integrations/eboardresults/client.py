
import requests
import hashlib
import re
import json



from app.core.config import settings
from app.integrations.eboardresults.exceptions import (
    EBoardConnectionError,
    EBoardResponseError,
)


class EBoardResultsClient:

    def __init__(self):
        self.base_url = settings.EBR_BASE_URL.rstrip("/")
        self.session = requests.Session()

        self.headers = {
            "User-Agent": "BD-Board-Result-API/1.0",
            "Accept": "application/json, text/html",
        }

    def get_page(self, path: str = "/v2/home"):
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            print("1st res send")
            resp = self.session.get(f"{self.base_url}/v2/home")

            if "bpanel.challenge" in resp.text or "Verifying you are not a robot" in resp.text:
                print("Challenge detected. Extracting parameters...")
                
                # Extract the 'challenge' object from script tag
                match = re.search(r"var\s+challenge\s*=\s*(\{.*?\});", resp.text)
                if not match:
                    raise ValueError("Could not extract challenge object from page source.")
                    
                challenge_data = json.loads(match.group(1))
                seed = str(challenge_data["seed"])
                salt = challenge_data["salt"]
                token = challenge_data["token"]
                
                # Replicate JavaScript SHA-256 calculation
                # JS logic: 'browser-proof:' + seed + ':' + salt
                input_str = f"browser-proof:{seed}:{salt}".encode('utf-8')
                computed_hash = hashlib.sha256(input_str).hexdigest()
                answer = f"hash:{computed_hash}"
                
                print(f"Computed Proof-of-Work: {answer}")
                
                # Step 2: Post proof to verification endpoint
                verify_url = f"{self.base_url}/_challenge-verify"
                verify_payload = {
                    "token": token,
                    "answer": answer
                }
                
                verify_resp = self.session.post(verify_url, json=verify_payload)
                print(f"Verification status: {verify_resp.status_code}")
                
                if verify_resp.status_code == 200 and verify_resp.json().get("ok"):
                    print("Challenge solved! Fetching homepage again...")
                    
                    # Step 3: Fetch protected target endpoint with validated session
                    home_resp = self.session.get(
                        url, 
                        headers=self.headers, 
                        timeout=settings.REQUEST_TIMEOUT
                        )
                    print(f"Homepage HTTP Status: {home_resp.status_code}")
                    
                    with open("homepage.html", "w", encoding="utf-8") as f:
                        f.write(home_resp.text)
                    print("Successfully saved actual homepage HTML.")
                else:
                    print("Verification rejected by server.")
            else:
                print("Direct access granted without challenge.")
            print("Send client Req")
            
            # response = self.session.get(
            #     url,
            #     headers=self.headers,
            #     timeout=settings.REQUEST_TIMEOUT,
            # )

            # print("Res client Req")

            home_resp.raise_for_status()
            # print(home_resp.text)
            return home_resp

        except requests.Timeout as exc:
            raise EBoardConnectionError(
                "The external website request timed out."
            ) from exc

        except requests.ConnectionError as exc:
            raise EBoardConnectionError(
                "Could not connect to the external website."
            ) from exc

        except requests.HTTPError as exc:
            raise EBoardResponseError(
                f"External website returned HTTP {home_resp.status_code}."
            ) from exc

    def close(self):
        self.session.close()
