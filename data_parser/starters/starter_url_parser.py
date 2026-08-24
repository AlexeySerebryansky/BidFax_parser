import json
from pathlib import Path

from brightdata_client.bright_data_client import BrightDataClient
from database.repository import add_car_urls
from database.session_manager import get_session

from url_parser.modules.get_lot_url import LotURLParser
from url_parser.modules.page_iterator import PageIterator
from url_parser.modules.url_batcher import UrlBatcher
from url_parser.modules.progress_manager import ProgressManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRANDS_FILE = PROJECT_ROOT / "data_parser" / "brands_models.json"
PROGRESS_FILE = PROJECT_ROOT / "data_parser" / "url_parser" / "progress.json"


def load_brands(path: Path) -> dict[str, list[str]]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def choose_brand_and_model(brands: dict[str, list[str]]) -> tuple[str, str]:
    print("\nChoose a brand:")

    brand_names = list(brands.keys())

    for i, brand in enumerate(brand_names, start=1):
        print(f"{i} - {brand}")

    while True:
        try:
            choice = int(input("> "))

            if 1 <= choice <= len(brand_names):
                brand = brand_names[choice - 1]
                break

            print("Invalid choice. Try again.")

        except ValueError:
            print("Please enter a number.")

    models = brands[brand]

    print(f"\nChoose a model for {brand}:")

    for i, model in enumerate(models, start=1):
        print(f"{i} - {model}")

    while True:
        try:
            choice = int(input("> "))

            if 1 <= choice <= len(models):
                model = models[choice - 1]
                break

            print("Invalid choice. Try again.")

        except ValueError:
            print("Please enter a number.")

    return brand, model


def choose_start_config(progress: ProgressManager) -> tuple[str | None, str | None, int]:
    print(
        "\n" +
        "\n".join([
            "=" * 60,
            "Choose starting point:",
            "=" * 60,
            "1 - Start over",
            "2 - Start from last stop:"
        ])
    )

    saved_progress = progress.get_progress()

    brand, model, page = saved_progress

    print(
        f"    Resuming from: "
        f"{brand}/{model}, page={page}"
    )


    while True:
        choice = input("> ")

        if choice == "1":
            return None, None, 0

        if choice == "2":

            if saved_progress is None:
                print("No saved progress found. Starting from the beginning.")
                return None, None, 0

            return brand, model, page

        print("Invalid choice. Enter 1 or 2.")


def process_model(
        progress: ProgressManager,
        parser: LotURLParser,
        brand: str,
        model: str,
        start_page: int = 1,
        stop_page: int = None,
        batch_size: int = 100
) -> None:
    print("=" * 60)
    print(f"[MODEL] Starting {brand}/{model}")
    print(f"[START] page={start_page}")
    print("=" * 60)

    iterator = PageIterator(
        parser=parser,
        brand=brand,
        model=model,
        start_page=start_page,
        stop_page=stop_page

    )

    batcher = UrlBatcher(
        iterator=iterator,
        batch_size=batch_size,
    )

    total_urls = 0

    while True:

        urls = batcher.next_batch()

        if urls is None:
            break

        with get_session() as session:
            add_car_urls(
                session=session,
                urls=urls,
            )

        progress.save_progress(
            brand=brand,
            model=model,
            page=iterator.page,
        )

        total_urls += len(urls)

        print(
            f"[MAIN] {brand}/{model} | "
            f"saved batch={len(urls)} | "
            f"total={total_urls}"
        )

    print(
        "\n" +
        "\n".join([
            f"[MODEL] Finished {brand}/{model} | "
            f"total={total_urls}\n",
            "=" * 60
        ])
    )


def starter():
    client = BrightDataClient()

    brands = load_brands(BRANDS_FILE)

    progress = ProgressManager(PROGRESS_FILE)

    parser =  LotURLParser(client=client)

    print(
        "\n" +
        "\n".join([
            "=" * 60,            "Choose stop page:",
            "=" * 60
        ])
    )
    stop_page = int(input("> "))

    print(
        "\n" +
        "\n".join([
            "=" * 60,
            "Choose batch size for push in database:",
            "=" * 60
        ])
    )
    batch_size = int(input("> "))

    print(
        "\n" +
        "\n".join([
            "=" * 60,
            "Choose mode:",
            "=" * 60,
            "1 - Process one model",
            "2 - Process all models"
        ])
    )

    while True:
        mode = input("> ")

        if mode in ("1", "2"):
            break

        print("Invalid choice. Enter 1 or 2.")

    resume_brand, resume_model, last_page = choose_start_config(progress)

    # ==================================================
    # PROCESS ONE MODEL
    # ==================================================

    if mode == "1":
        brand, model = choose_brand_and_model(brands)

        if resume_brand is not None:
            print(
                "\n"
                "[WARNING] Resume mode is only useful "
                "when processing all models."
            )

        process_model(
            progress=progress,
            parser=parser,
            brand=brand,
            model=model,
            start_page=last_page + 1,
            stop_page=stop_page,
            batch_size=batch_size
        )

        return

    # ==================================================
    # PROCESS ALL MODELS
    # ==================================================

    resume = resume_brand is not None

    for brand, models in brands.items():

        if resume and brand != resume_brand:
            continue

        print(f"\n[BRAND] Starting: {brand}")

        start_page = last_page + 1

        for model in models:

            if resume:
                if model != resume_model:
                    continue
                resume = False

            try:
                process_model(
                    progress=progress,
                    parser=parser,
                    brand=brand,
                    model=model,
                    start_page=start_page,
                    stop_page=stop_page,
                    batch_size=batch_size
                )

                start_page = 1
            except Exception as e:
                print(
                    "\n"
                    f"[MAIN] ERROR "
                    f"{brand}/{model}: {e}"
                )

                continue


starter()
