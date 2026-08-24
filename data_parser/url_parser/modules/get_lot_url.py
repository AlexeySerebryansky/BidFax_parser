from bs4 import BeautifulSoup

BASE_URL = "https://bidfax.info/"


class LotURLParser:

    def __init__(self, client):
        self.client = client

    def _get_html(self, url: str) -> str:
        html = self.client.get_html(url)
        return html

    def _get_soup(self, html: str) -> BeautifulSoup:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )
        return soup

    def _list_car_urls(self, soup: BeautifulSoup) -> list | None:

        links = soup.select(
            "#grid .thumbnail.offer .caption a[href]"
        )

        lot_urls = []

        for link in links:

            href = link.get("href")

            if not href:
                continue

            lot_urls.append(href)

        return lot_urls

    def get_lot_urls(self, brand: str, model: str, page: int) -> list[str]:

        url = f"{BASE_URL}{brand}/{model}/page/{page}/"

        print(
            f"\n[LOTS] Getting URLs: {BASE_URL}{brand}/{model}/page/{page}/"
        )

        counter = 0

        while True:
            counter += 1

            html = self._get_html(url)
            soup = self._get_soup(html)

            lot_urls = self._list_car_urls(soup)

            if lot_urls:
                print(
                    f"[LOTS] Found: {len(lot_urls)} URLs"
                )
                return list(dict.fromkeys(lot_urls))

            print(
                f"[LOTS] No URLs found. Loop {counter} starting"
            )
