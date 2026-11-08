
from bs4 import BeautifulSoup


def parse_result_html(html: str) -> dict:
    """
    Parse an authorized HTML result response.

    The actual field selectors will be added after
    examining a permitted sample response.
    """

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else None

    return {
        "page_title": title,
        "parsed": False,
        "message": "Result parsing rules are not configured yet."
    }
