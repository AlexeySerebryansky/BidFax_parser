import json
from pathlib import Path

from car_lot_parser.brand_repository import BrandRepository
from car_lot_parser.lot_parser import LotParser

BASE_DIR = Path(__file__).resolve().parent.parent

BRANDS_FILE = BASE_DIR / "data_parser" / "brands_models.json"

HTML_FILE = (
    BASE_DIR
    / "tests"
    / "test_html_pages"
    / "Acura Adx A-Spec 2025 White 1.5L vin_ 3HDSA1H5XSM709951 free car history.html"
)



with open(HTML_FILE, "r", encoding="utf-8") as file:
    html = file.read()

brand_repository = BrandRepository(BRANDS_FILE)
parser = LotParser(brand_repository)

result = parser.parse(html)

print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
        default=str,
    )
)
