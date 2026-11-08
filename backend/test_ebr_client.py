from bs4 import BeautifulSoup
from app.integrations.eboardresults.client import EBoardResultsClient
from app.integrations.eboardresults.exceptions import EBoardResultsError

client = EBoardResultsClient()

try:
    response = client.get_page()

    print("Final URL:", response.url)
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Page Title:", BeautifulSoup(response.text, "html.parser").title)
    print("Response Length:", len(response.text))
    print("Preview:", response.text[:500])

except EBoardResultsError as error:
    print("Integration error:", error)

finally:
    client.close()
