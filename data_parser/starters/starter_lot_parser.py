from pathlib import Path

from car_lot_parser.orchestrator import Orchestrator
from car_lot_parser.lot_parser import LotParser
from car_lot_parser.brand_repository import BrandRepository
from car_lot_parser.db_writer import DBWriter
from car_lot_parser.batcher import CarBatcher

from database import repository, session_manager

from gologin_client.go_login_client import GoLoginClient


def run():
    print("[MAIN] Starting Lot Parser\n")


    print("Starting reset locked cars")

    with session_manager.get_session() as session:
        reset_count = repository.reset_locked_cars(session)
        session.commit()

    print(f"Reset {reset_count} locked cars")

    BRANDS_FILE = Path(__file__).parent.parent / "brands_models.json"

    brand_repository = BrandRepository(BRANDS_FILE)
    parser = LotParser(brand_repository)

    print(
        "\n" +
        "\n".join([
            "=" * 60,
            "Choose batch size to get from DB for worker:",
            "=" * 60
        ])
    )

    batch_size = int(input("> "))

    batcher = CarBatcher(
        session_factory=session_manager.get_session,
        batch_size=batch_size,
    )

    db_writer = DBWriter(
        session_factory=session_manager.get_session,
    )

    print(
        "\n" +
        "\n".join([
            "=" * 60,
            "Choose count of workers:",
            "=" * 60
        ])
    )

    workers_count = int(input("> "))

    orchestrator = Orchestrator(
        client_factory=GoLoginClient,
        parser=parser,
        db_writer=db_writer,
        batcher=batcher,
        workers_count=workers_count
    )

    print(
        "\n" +
        "\n".join([
            "=" * 60,
            f"Start workers: {workers_count} with batch size: {batch_size}",
            "=" * 60
        ])
    )

    orchestrator.run()

if __name__ == "__main__":
    run()
