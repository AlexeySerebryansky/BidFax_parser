from url_parser.page_iterator import PageIterator


class UrlBatcher:

    def __init__(self, iterator: PageIterator, batch_size: int = 100):
        self.iterator = iterator
        self.batch_size = batch_size
        self.pending_urls: list[str] = []

    def next_batch(self) -> list[str] | None:

        batch_urls: list[str] = []

        while len(batch_urls) < self.batch_size:

            if self.pending_urls:
                remaining = self.batch_size - len(batch_urls)

                batch_urls.extend(
                    self.pending_urls[:remaining]
                )

                self.pending_urls = self.pending_urls[remaining:]

                continue

            urls = self.iterator.next_page()

            if urls is None:
                break

            remaining = self.batch_size - len(batch_urls)

            batch_urls.extend(
                urls[:remaining]
            )

            self.pending_urls.extend(
                urls[remaining:]
            )

        if not batch_urls:
            return None

        print(
            f"[BATCHER] "
            f"{self.iterator.brand}/{self.iterator.model} | "
            f"batch={len(batch_urls)} | "
            f"pending={len(self.pending_urls)}"
        )

        return batch_urls
