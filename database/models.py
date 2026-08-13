from datetime import datetime


from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Integer,
    SmallInteger,
    String,
    Text,
    text
)

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
    )

    vin: Mapped[str | None] = mapped_column(
        String(17),
        index=True
    )

    auction: Mapped[str | None] = mapped_column(String(50))
    lot_number: Mapped[int | None] = mapped_column(String(50))
    sale_date: Mapped[Date | None] = mapped_column(Date)

    year: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[str | None] = mapped_column(Text)

    engine: Mapped[str | None] = mapped_column(Text)
    mileage: Mapped[int | None] = mapped_column(Integer)
    mileage_status: Mapped[str | None] = mapped_column(Text)
    seller: Mapped[str | None] = mapped_column(Text)
    documents: Mapped[str | None] = mapped_column(Text)
    sale_location: Mapped[str | None] = mapped_column(Text)

    primary_damage: Mapped[str | None] = mapped_column(Text)
    secondary_damage: Mapped[str | None] = mapped_column(Text)

    estimated_value: Mapped[int | None] = mapped_column(Integer)
    repair_cost: Mapped[int | None] = mapped_column(Integer)

    transmission: Mapped[str | None] = mapped_column(Text)
    body_color: Mapped[str | None] = mapped_column(Text)
    drive: Mapped[str | None] = mapped_column(Text)
    fuel: Mapped[str | None] = mapped_column(Text)
    keys: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)

    final_bid: Mapped[int | None] = mapped_column(Integer)

    photo_urls: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    previous_auctions: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
