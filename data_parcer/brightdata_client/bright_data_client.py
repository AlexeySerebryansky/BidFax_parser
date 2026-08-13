import os

import requests
from dotenv import load_dotenv


load_dotenv()


class BrightDataClient:

    API_URL = "https://api.brightdata.com/request"

    def __init__(self):
        self.api_key = os.getenv("BRIGHTDATA_API_KEY")
        self.zone = os.getenv("BRIGHTDATA_ZONE")

        if not self.api_key:
            raise ValueError("BRIGHTDATA_API_KEY is not set")

        if not self.zone:
            raise ValueError("BRIGHTDATA_ZONE is not set")

    def get_html(self, url: str) -> str:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "zone": self.zone,
            "url": url,
            "format": "raw",        }

        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        print("STATUS:", response.status_code)

        if response.status_code != 200:
            print("RESPONSE:")
            print(response.text)

        response.raise_for_status()

        return response.text