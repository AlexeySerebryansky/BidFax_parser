from car_lot_parser.page_validator import PageValidator


class Worker:
    MAX_RETRIES = 3

    def __init__(self, client, parser, batcher, db_writer, worker_id):
        self.client = client
        self.parser = parser
        self.batcher = batcher
        self.db_writer = db_writer
        self.worker_id = worker_id

    def _get_valid_html(self, url: str) -> str | None:
        for attempt in range(1, self.MAX_RETRIES + 1):
            html = self.client.get_html(url)

            if PageValidator.is_valid(html):
                return html

            print(
                f"[WORKER ({self.worker_id})] Invalid page: {url}. "
                f"Retry {attempt}/{self.MAX_RETRIES}"
            )

        print(
            f"[WORKER ({self.worker_id})] Failed to get valid page: {url}"
        )

        return None

    def _process_url(self, car_id: int, url: str) -> dict:
        html = self._get_valid_html(url)

        if html is None:
            return {
                "id": car_id,
                "url": url,
            }

        result = self.parser.parse(html)
        result["id"] = car_id
        result["url"] = url

        return result

    def run(self) -> None:
        print(f"[WORKER ({self.worker_id})] Started")
        try:
            while True:

                batch = self.batcher.next_batch()

                if batch is None:
                    print(f"[WORKER ({self.worker_id})] No more cars to process")
                    break

                print(f"[WORKER ({self.worker_id})] reserved {len(batch)} cars")

                results = []

                for car_id, url in batch:
                    print(f"[WORKER ({self.worker_id})] car id - {car_id} in processing. URL: {url}")
                    try:
                        result = self._process_url(
                            car_id,
                            url,
                        )

                        print(f"[WORKER ({self.worker_id})] car id - {car_id} done")

                    except Exception as exc:
                        print(
                            f"[WORKER ({self.worker_id})] Error processing "
                            f"{exc}"
                        )

                        result = {
                            "id": car_id,
                            "url": url,
                        }

                    results.append(result)

                self.db_writer.write(results)

                print(
                    f"[WORKER ({self.worker_id})] wrote results to database. ",
                    flush=True,
                )

        finally:
            print(f"[WORKER ({self.worker_id})] Finished and closing")
            self.client.close()

        print(f"[WORKER ({self.worker_id})] closed")
