from sqlalchemy.orm import Session
from database.models import Car


def add_car(session: Session, car: Car) -> None:
    session.add(car)


def add_cars(session: Session, cars: list[Car]) -> None:
    session.add(cars)


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
