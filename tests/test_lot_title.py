from data_parcer.brightdata_client.bright_data_client import BrightDataClient
from url_parser.get_lot_url import LotParser


def test_lot_title():
    client = BrightDataClient()
    parser = LotParser(client)

    urls = parser.get_lot_urls(
        brand="acura",
        model="adx",
        page=3
    )

    print("="*60)
    print(f"FOUND: {len(urls)} URLs")
    print("="*60)

    for i, url in enumerate(urls, start=1):
        print(f"[{i}] {url}")


test_lot_title()