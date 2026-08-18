from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from database.models import Car


def add_car(session: Session, car: Car) -> None:
    session.add(car)


def add_cars(session: Session, cars: list[Car]) -> None:
    session.add(cars)

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


def delete_car_by_url(session: Session, url: str) -> None:
    car = session.query(Car).filter(
        Car.url == url
    ).first()

    if car:
        session.delete(car)
