import json
from pathlib import Path

from car_parser import CarParser

OUTPUT_FILE = Path("brands_models.json")

print("=" * 60)
print("START MODELS COLLECTION")
print("=" * 60)

parser = CarParser()

# Загружаем уже собранные бренды
with OUTPUT_FILE.open("r", encoding="utf-8") as f:
    brands_models = json.load(f)

brands = list(brands_models.keys())

print(f"[PIPELINE] Brands to process: {len(brands)}")
print()

for index, brand in enumerate(brands, start=1):

    if brands_models[brand]:
        print(
            f"[{index}/{len(brands)}] "
            f"{brand}: already has {len(brands_models[brand])} models -> SKIP"
        )
        continue

    print(
        f"[{index}/{len(brands)}] "
        f"{brand}: getting models..."
    )

    try:
        models = parser.get_models(brand)

        brands_models[brand] = models

        # Сохраняем сразу после каждого бренда
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(
                brands_models,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[{index}/{len(brands)}] "
            f"{brand}: FOUND {len(models)} models"
        )

    except Exception as e:
        print(
            f"[{index}/{len(brands)}] "
            f"{brand}: ERROR -> {e}"
        )

        # Ничего не записываем в этот бренд.
        # Следующий запуск попробует его снова.
        continue

    print()

print("=" * 60)
print("MODELS COLLECTION FINISHED")
print("=" * 60)
