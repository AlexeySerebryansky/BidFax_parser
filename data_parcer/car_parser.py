from bs4 import BeautifulSoup
from urllib.parse import urlparse

from data_parcer.bright_data_client import BrightDataClient


BASE_URL = "https://bidfax.info/"


class CarParser:

    def __init__(self):
        self.client = BrightDataClient()

    def get_brands(self) -> list[str]:

        print("[BRANDS] Getting brands...")

        html = self.client.get_html(BASE_URL)

        soup = BeautifulSoup(html, "html.parser")

        menu = soup.select_one(".drop-menu-main-sub")

        if not menu:
            raise RuntimeError("Brand menu not found")

        brands = []

        for link in menu.select("a[href]"):

            href = link["href"]
            path = urlparse(href).path.strip("/")

            if not path:
                continue

            if "/" in path:
                continue

            brands.append(path)

        brands = list(dict.fromkeys(brands))

        print(f"[BRANDS] Found: {len(brands)}")

        return brands

    def get_models(self, brand: str) -> list[str]:

        print(f"[MODEL] Getting models for: {brand}")

        url = f"{BASE_URL}{brand}/"

        print(f"[MODEL] URL: {url}")

        html = self.client.get_html(url)

        soup = BeautifulSoup(html, "html.parser")

        menus = soup.select(".drop-menu-main-sub")

        if len(menus) < 2:
            raise RuntimeError(
                f"Model menu not found for brand: {brand}"
            )
        # We will take second menu beacuse at fist saved cars brand

        menu = menus[1]

        models = []

        for link in menu.select("a[href]"):

            href = link.get("href")

            if not href:
                continue

            href = href.strip("/")

            parts = href.split("/")

            if len(parts) != 2:
                continue

            brand_slug, model_slug = parts

            if brand_slug != brand:
                continue

            models.append(model_slug)

        models = list(dict.fromkeys(models))

        print(
            f"[MODEL] {brand}: {len(models)} models"
        )

        return models