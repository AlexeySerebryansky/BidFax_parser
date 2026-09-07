from pathlib import Path

from client.brightdata_client import BrightDataClient
from car_lot_parser.batcher import CarBatcher
from car_lot_parser.brand_repository import BrandRepository
from car_lot_parser.lot_parser import LotParser
from car_lot_parser.db_writer import DBWriter
from car_lot_parser.car_worker import Worker

from database import get_session

brands_path = Path(__file__).parent.parent.parent /"data_parser" / "brands_models.json"

print("[MAIN] Starting")

client = BrightDataClient()

brand_repository = BrandRepository(brands_path)
parser = LotParser(brand_repository)

batcher = CarBatcher(
    session_factory=get_session,
    batch_size=2,
)

db_writer = DBWriter(
    session_factory=get_session,
)

worker = Worker(
    client=client,
    parser=parser,
    batcher=batcher,
    db_writer=db_writer,
)

print("[MAIN] Starting worker")

worker.run()
