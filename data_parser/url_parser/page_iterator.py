from url_parser.get_lot_url import LotParser


class PageIterator:

    def __init__(self,
                 parser: LotParser,
                 brand: str,
                 model: int,
                 max_attempts: int = 2,
                 start_page: int = 1,
                 stop_page: int = None):

        self.parser = parser
        self.brand = brand
        self.model = model
        self.max_attempts = max_attempts
        self.start_page = start_page
        self.stop_page = stop_page

        self.page = 1

    def next_page(self) -> list | None:

        for attempt in range(1, self.max_attempts + 1):

            while self.page <= self.stop_page:

                try:
                    urls = self.parser.get_lot_urls(
                        brand=self.brand,
                        model=self.model,
                        page=self.page
                    )

                    self.page += 1

                    return urls

                except Exception as e:

                    print(
                        f"[ITERATOR] "
                        f"{self.brand}/{self.model} | "
                        f"page={self.page} | "
                        f"attempt={attempt}/{self.max_attempts} | "
                        f"ERROR: {e}"
                    )

                print(
                    f"[ITERATOR] "
                    f"{self.brand}/{self.model} | "
                    f"page={self.page} | "
                    f"FAILED after {self.max_attempts} attempts"
                )

                return None
            return None
        return None

    def reset_page(self):
        self.page = 1
