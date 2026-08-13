from brightdata_client.bright_data_client import BrightDataClient
from url_parser.get_lot_url import LotParser
from url_parser.page_iterator import PageIterator


def test_page_iterator():

    client = BrightDataClient()
    parser = LotParser(client)

    iterator = PageIterator(
        parser=parser,
        brand="acura",
        model="adx",
        max_attempts=2,
    )

    print("=" * 60)
    print("PAGE ITERATOR TEST")
    print("=" * 60)

    for i in range(3):

        print(f"\n[TEST] Request #{i + 1}")

        urls = iterator.next_page()

        if urls is None:
            print("[STOP] Iterator returned None")
            break

        print(f"[OK] Received {len(urls)} URLs")

        for url in urls:
            print(f"    {url}")

        print(f"[OK] Next page: {iterator.page}")

    print("\n" + "=" * 60)
    print("TEST FINISHED")
    print("=" * 60)


test_page_iterator()