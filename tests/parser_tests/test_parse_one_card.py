import json
from pathlib import Path


from client.brightdata_client import BrightDataClient
from car_lot_parser.brand_repository import BrandRepository
from car_lot_parser.lot_parser import LotParser

BASE_DIR = Path(__file__).resolve().parent.parent.parent

BRANDS_FILE = (
        BASE_DIR
        / "data_parser"
        / "brands_models.json"
)

URL = "https://en.bidfax.info/acura/adx/38875390-acura-adx-2026-silver-15l-4-vin-3hdsa1h33tm702128.html"

client = BrightDataClient()

brand_repository = BrandRepository(
    BRANDS_FILE
)

parser = LotParser(
    brand_repository
)

html = client.get_html(URL)

print("HTML length:", len(html))

print(
    "short-story:",
    "short-story" in html
)

print(
    "Auction:",
    "Auction:" in html
)

print(
    "Lot number:",
    "Lot number:" in html
)

print(
    "Estimated retail value:",
    "Estimated retail value:" in html
)

result = parser.parse(html)

print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
        default=str,
    )
)
