from database.models import Car
from url_parser.url_batcher import UrlBatcher


class FakeIterator:

    def __init__(self):
        self.brand = "test"
        self.model = "test"
        self.page = 1

        self.pages = [
            [
                "url_1",
                "url_2",
                "url_3",
                "url_4",
                "url_5",
                "url_6",
                "url_7",
                "url_8",
                "url_9",
                "url_10",
            ],
            [
                "url_11",
                "url_12",
                "url_13",
                "url_14",
                "url_15",
                "url_16",
                "url_17",
                "url_18",
                "url_19",
                "url_20",
            ],
            [
                "url_21",
                "url_22",
                "url_23",
                "url_24",
                "url_25",
                "url_26",
                "url_27",
                "url_28",
                "url_29",
                "url_30",
            ],
        ]

    def next_page(self):

        if not self.pages:
            return None

        urls = self.pages.pop(0)
        self.page += 1

        return urls


def test_car_batcher():

    iterator = FakeIterator()

    batcher = UrlBatcher(
        iterator=iterator,
        batch_size=25
    )

    # --------------------------------------------------
    # BATCH 1
    # --------------------------------------------------

    batch = batcher.next_batch()

    assert batch is not None
    assert len(batch) == 25

    assert all(
        isinstance(car, Car)
        for car in batch
    )

    print("[OK] Batch 1: 25 cars")

    assert len(batcher.pending_urls) == 5

    print("[OK] Pending after batch 1: 5")

    # --------------------------------------------------
    # BATCH 2
    # --------------------------------------------------

    batch = batcher.next_batch()

    assert batch is not None
    assert len(batch) == 5

    print("[OK] Batch 2: 5 cars")

    assert len(batcher.pending_urls) == 0



print("=" * 60)
print("CAR BATCHER TEST")
print("=" * 60)

test_car_batcher()

print("=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)