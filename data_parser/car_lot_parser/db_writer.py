from database import Car


class DBWriter:

    DATA_FIELDS = {
        column.name
        for column in Car.__table__.columns
        if column.name not in {
            "id",
            "worker_status",
            "created_at",
        }
    }

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def write(self, results: list[dict]) -> None:
        if not results:
            return

        with self.session_factory() as session:

            for result in results:
                car_id = result["id"]

                data = {
                    field: result.get(field)
                    for field in self.DATA_FIELDS
                }

                data["worker_status"] = "free"

                session.query(Car).filter(
                    Car.id == car_id
                ).update(
                    data,
                    synchronize_session=False,
                )

            session.commit()