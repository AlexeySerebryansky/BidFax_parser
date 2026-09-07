from sqlalchemy import or_, select

from database import Car


class CarBatcher:

    REQUIRED_FIELDS = {
        "brand",
        "model",
        "auction",
        "lot_number",
        "sale_date",
        "year",
        "vin",
        "final_bid"
    }

    def __init__(self, session_factory, batch_size: int = 20):
        self.session_factory = session_factory
        self.batch_size = batch_size

    def next_batch(self) -> list[tuple[int, str]] | None:

        with self.session_factory() as session:

            required_columns = [
                getattr(Car, field)
                for field in self.REQUIRED_FIELDS
            ]

            has_null = or_(
                *[
                    column.is_(None)
                    for column in required_columns
                ]
            )

            stmt = (
                select(Car)
                .where(
                    Car.worker_status == "free",
                    has_null,
                )
                .with_for_update(skip_locked=True)
                .limit(self.batch_size)
            )

            cars = session.scalars(stmt).all()

            if not cars:
                return None

            batch = [
                (car.id, car.url)
                for car in cars
            ]

            for car in cars:
                car.worker_status = "lock"

            session.commit()

        print(
            f"[BATCHER] "
            f"Reserved {len(batch)} cars"
        )

        return batch
