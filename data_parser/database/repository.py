from sqlalchemy import inspect, update, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from database.models import Car

def reset_locked_cars(session: Session) -> int:
    stmt = (
        update(Car)
        .where(Car.worker_status == "lock")
        .values(worker_status="free")
    )

    result = session.execute(stmt)

    return result.rowcount

def add_car(session: Session, car: Car) -> None:
    session.add(car)


def add_cars(session: Session, cars: list[Car]) -> None:
    session.add_all(cars)


def add_car_urls(session: Session, urls: list[str]) -> None:
    if not urls:
        return

    stmt = (
        insert(Car)
        .values([
            {"url": url}
            for url in urls
        ])
        .on_conflict_do_nothing(
            index_elements=[Car.url]
        )
    )

    session.execute(stmt)


def get_car_by_url(session: Session, url: str) -> Car | None:
    return session.query(Car).filter(
        Car.url == url
    ).first()


def get_car_by_id(session: Session, car_id: int) -> Car | None:
    return session.query(Car).filter(
        Car.id == car_id
    ).first()


def get_lock_free_cars(session: Session, batch_size: int) -> list[Car] | None:

    columns = [
        column
        for column in inspect(Car).mapper.column_attrs
        if column.key not in {
            "id",
            "url",
            "worker_status",
            "created_at",
        }
    ]

    cars = (
        session.query(Car)
        .filter(
            Car.worker_status == "free",
            or_(
                *[
                    column.columns[0].is_(None)
                    for column in columns
                ]
            ),
        )
        .order_by(Car.id)
        .with_for_update(skip_locked=True)
        .limit(batch_size)
        .all()
    )

    for car in cars:
        car.worker_status = "lock"

    return cars


def delete_car_by_url(session: Session, url: str) -> None:
    car = session.query(Car).filter(
        Car.url == url
    ).first()

    if car:
        session.delete(car)
