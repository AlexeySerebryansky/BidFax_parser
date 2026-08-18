from bs4 import BeautifulSoup

BASE_URL = "https://bidfax.info/"


class LotParser:

    def __init__(self, client):
        self.client = client

    def get_lot_urls(self, brand: str, model: str, page: int) -> list[str]:

        url = f"{BASE_URL}{brand}/{model}/page/{page}/"

        print(
            f"[LOTS] Getting URLs: "
            f"{BASE_URL}{brand}/{model}/page/{page}/"
        )

        html = self.client.get_html(url)

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        links = soup.select(
            "#grid .thumbnail.offer .caption a[href]"
        )

        lot_urls = []

        for link in links:

            href = link.get("href")

            if not href:
                continue

            lot_urls.append(href)

        lot_urls = list(dict.fromkeys(lot_urls))

        print(
            f"[LOTS] Found: {len(lot_urls)} URLs"
        )

        return lot_urls
