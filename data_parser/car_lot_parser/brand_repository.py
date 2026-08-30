import json


class BrandRepository:

    def __init__(self, path: str):

        with open(path, "r", encoding="utf-8") as file:
            brands = json.load(file)

        self.brands = sorted(
            brands.keys(),
            key=lambda brand: len(brand.split()),
            reverse=True,
        )

    def find_brand(self, parts: list[str]) -> str | None:

        for brand in self.brands:

            brand_parts = brand.split()

            if [
                part.lower()
                for part in parts[:len(brand_parts)]
            ] == [
                part.lower()
                for part in brand_parts
            ]:
                return brand

        return None
