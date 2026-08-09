import json
from pathlib import Path
from car_parser import CarParser


OUTPUT_FILE = Path("brands_models.json")

print("=" * 60)
print("BRANDS COLLECTION")
print("=" * 60)

parser = CarParser()

brands = parser.get_brands()

print(f"[BRANDS] Found: {len(brands)}")

data = {
    brand: []
    for brand in brands
}

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=4
    )

print(f"[BRANDS] Saved to: {OUTPUT_FILE}")
print("=" * 60)
print("DONE")
