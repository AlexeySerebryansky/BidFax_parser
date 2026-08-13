from database.session_manager import _session_factory
from database.models import Car
from database.repository import (
    add_car,
    get_car_by_url,
    delete_car_by_url,
)

TEST_URL = "https://bidfax.info/test/database-smoke-test/"


def test():
    print("=" * 60)
    print("DATABASE SMOKE TEST")
    print("=" * 60)

    with _session_factory() as session:

        try:
            # --------------------------------------------------
            # 1. INSERT
            # --------------------------------------------------

            print("\n[1] Creating test car...")

            car = Car(
                url=TEST_URL,
                auction="Copart",
                lot_number="99999999",
                year=2020,
                vin="TESTVIN123456789",
                status="Run and Drive",
                engine="3.0L 6",
                mileage=50000,
                mileage_status="Actual",
                seller="Test Seller",
                documents="Test Document",
                sale_location="Test Location",
                primary_damage="Front End",
                secondary_damage="None",
                estimated_value=20000,
                repair_cost=3000,
                transmission="Automatic",
                body_color="Black",
                drive="Rear-Wheel Drive",
                fuel="Gas",
                keys="Yes",
                note="Database smoke test",
                final_bid=12000,
                photo_urls=[
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg",
                ],
                previous_auctions=[
                    "https://bidfax.info/test/previous/1/",
                ],
            )

            add_car(session, car)
            session.commit()

            print("[OK] INSERT successful")

            # --------------------------------------------------
            # 2. SELECT
            # --------------------------------------------------

            print("\n[2] Reading test car...")

            saved_car = get_car_by_url(session, TEST_URL)

            if saved_car is None:
                raise RuntimeError(
                    "Test car was not found in database"
                )

            print("[OK] SELECT successful")

            print(f"    ID:  {saved_car.id}")
            print(f"    VIN: {saved_car.vin}")
            print(f"    URL: {saved_car.url}")


            # --------------------------------------------------
            # 3. DELETE
            # --------------------------------------------------


            print("\n[3] Deleting test car...")

            delete_car_by_url(session, TEST_URL)

            session.commit()

            deleted_car = get_car_by_url(
                session,
                car.url
            )

            if deleted_car is not None:
                raise RuntimeError(
                    "Test car still exists in database"
                )

            print("[OK] DELETE successful")

            # --------------------------------------------------
            # 4. VERIFY DELETE
            # --------------------------------------------------

            print("\n[4] Verifying deletion...")

            deleted_car = get_car_by_url(session, TEST_URL)

            if deleted_car is not None:
                raise RuntimeError(
                    "Test car still exists in database"
                )

            print("[OK] Record successfully removed")

            print("\n" + "=" * 60)
            print("DATABASE SMOKE TEST PASSED")
            print("=" * 60)

        except Exception:
            session.rollback()
            raise


test()
