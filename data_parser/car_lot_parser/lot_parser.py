import re
from datetime import datetime

from bs4 import BeautifulSoup

from car_lot_parser.brand_repository import BrandRepository


class LotParser:
    FIELD_MAP = {
        "Auction": "auction",
        "Lot number": "lot_number",
        "Date of sale": "sale_date",
        "Year": "year",
        "VIN": "vin",
        "Condition": "status",
        "Engine": "engine",
        "Mileage": "mileage",
        "Seller": "seller",
        "Documents": "documents",
        "Location": "sale_location",
        "Primary Damage": "primary_damage",
        "Secondary Damage": "secondary_damage",
        "Estimated Retail Value": "estimated_value",
        "Estimated Repair Cost": "repair_cost",
        "Transmission": "transmission",
        "Body color": "body_color",
        "Drive": "drive",
        "Fuel": "fuel",
        "Keys": "keys",
        "Notes": "note",
        "Final bid": "final_bid",
    }
    BASE_URL = "/bidfax.info"

    def __init__(self, brand_repository: BrandRepository):
        self.brand_repository = brand_repository

    @staticmethod
    def _get_soup(html: str) -> BeautifulSoup:
        return BeautifulSoup(
            html,
            "html.parser",
        )

    def _parse_short_story(self, soup: BeautifulSoup) -> dict:
        data = {}

        blocks = soup.select("p.short-story, p.short-story2")

        for block in blocks:

            label = block.find(string=True)

            if not label:
                continue

            label = re.sub(r"[\s:≈]+$", "", label)

            field = self.FIELD_MAP.get(label)

            if not field:
                continue

            value = block.get_text(
                " ",
                strip=True,
            )

            if value.startswith(label):
                value = value[len(label):].strip()

            value = value.removeprefix(":").strip()

            data[field] = value

        return self._normalize_short_story(data)

    def _normalize_short_story(self, data: dict) -> dict:

        if "sale_date" in data:
            data["sale_date"] = datetime.strptime(
                data["sale_date"],
                "%d.%m.%Y",
            ).date()

        if "year" in data:
            data["year"] = int(data["year"])

        if "lot_number" in data:
            data["lot_number"] = str(
                data["lot_number"]
            )

        if "mileage" in data:
            data["mileage"], data["mileage_status"] = (
                self._parse_mileage(data["mileage"])
            )

        for field in (
                "estimated_value",
                "repair_cost"
        ):
            if field in data:
                data[field] = self._parse_money(
                    data[field]
                )

        return data

    @staticmethod
    def _parse_mileage(value: str) -> tuple[int | None, str | None]:
        mileage_match = re.search(r"[\d,]+", value)

        if not mileage_match:
            return None, None

        mileage = int(mileage_match.group().replace(",", ""))

        status_match = re.search(r"\(([^)]+)\)", value)
        status = status_match.group(1).strip() if status_match else None

        return mileage, status

    @staticmethod
    def _parse_final_bid(soup: BeautifulSoup) -> int | None:
        value = soup.select_one(".bidfax-price .prices")

        if not value:
            return None

        return LotParser._parse_money(
            value.get_text(strip=True)
        )

    @staticmethod
    def _parse_money(value: str) -> int | None:

        match = re.search(r"\d[\d,]*(?:\.\d+)?", value)

        if not match:
            return None

        value = match.group().replace(",", "")

        return int(float(value))

    def _parse_brand_model(self, soup: BeautifulSoup) -> dict:
        title = soup.find("h1")

        if not title:
            return {
                "brand": None,
                "model": None,
            }

        title = title.get_text(" ", strip=True)
        parts = title.split()

        if not parts:
            return {
                "brand": None,
                "model": None,
            }

        brand = self.brand_repository.find_brand(parts)

        if not brand:
            return {
                "brand": None,
                "model": None,
            }

        brand_parts = brand.split()
        model_start = len(brand_parts)

        year_index = next(
            (
                index
                for index, part in enumerate(parts[model_start:], model_start)
                if part.isdigit()
                   and 1990 <= int(part) <= 2027
            ),
            None,
        )

        if year_index is None:
            return {
                "brand": brand,
                "model": None,
            }

        model = " ".join(
            parts[model_start:year_index]
        ).lower()

        return {
            "brand": brand,
            "model": model,
        }

    @staticmethod
    def _parse_images(soup: BeautifulSoup) -> list[str]:

        return list(dict.fromkeys(
            image["src"]
            for image in soup.find_all("img", src=True)
            if "/uploads/" in image["src"]
        ))

    @staticmethod
    def _parse_previous_auctions(soup: BeautifulSoup) -> dict[str, int | None]:
        result = []

        for lot in soup.select(
                ".anothersale ~ #grid .thumbnail.offer"
        ):
            price = lot.select_one(
                ".price .prices"
            )

            date = None

            for item in lot.select(
                    ".short-storyrel"
            ):
                text = item.get_text(" ", strip=True)

                if text.startswith("Date of sale:"):
                    date_element = item.select_one(
                        ".blackfont"
                    )

                    if date_element:
                        date = date_element.get_text(
                            strip=True
                        )

                    break

            if price and date:
                result.append({
                    price.get_text(strip=True): date
                })

        return result

    def parse(self, html: str) -> dict:
        soup = self._get_soup(html)

        return {
            **self._parse_short_story(soup),
            **self._parse_brand_model(soup),
            "final_bid": self._parse_final_bid(soup),
            "photo_urls": self._parse_images(soup),
            "previous_auctions": self._parse_previous_auctions(soup)
        }
