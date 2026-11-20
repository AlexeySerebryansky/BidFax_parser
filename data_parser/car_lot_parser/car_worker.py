from car_lot_parser.page_validator import (
    PageValidator,
    PageForbiddenError,
    PageNotFoundError,
    CloudflareError,
    InvalidPageError,
)
from time import sleep


class Worker:
    MAX_ERRORS  = 3
    CLOUDFLARE_TIMEOUT = 3

    def __init__(self, client, parser, batcher, db_writer, worker_id):
        self.client = client
        self.parser = parser
        self.batcher = batcher
        self.db_writer = db_writer
        self.worker_id = worker_id

        self.error_counts = {
            "invalid_page": 0,
            "cloudflare": 0,
            "not_found": 0,
            "forbidden": 0,
        }

        self._stop = False

        self._last_html = None
        self._last_url = None
        self._last_car_id = None

    # ------------------------------------------------------------------
    # Page processing
    # ------------------------------------------------------------------

    def _get_valid_html(self, url: str, car_id: int) -> str | None:
        html = self.client.get_html(url)

        self._last_html = html
        self._last_url = url
        self._last_car_id = car_id

        return PageValidator.validate(html)

    def _register_error(self, error_type: str) -> None:
        self.error_counts[error_type] += 1

        count = self.error_counts[error_type]

        print(
            f"[WORKER ({self.worker_id})] "
            f"{error_type} error "
            f"{count}/{self.MAX_ERRORS}",
            flush=True,
        )

        if count >= self.MAX_ERRORS:
            print(
                f"[WORKER ({self.worker_id})] "
                f"{self.MAX_ERRORS} consecutive "
                f"{error_type} errors. Stopping worker.",
                flush=True,
            )

            if error_type == "invalid_page" and self._last_html is not None:
                self._log_page_preview(
                    car_id=self._last_car_id,
                    url=self._last_url,
                    html=self._last_html,
                )

            self._stop = True

    def _reset_errors(self) -> None:
        for error_type in self.error_counts:
            self.error_counts[error_type] = 0

    def _log_page_preview(self, car_id: int, url: str, html: str) -> None:
        print(
            f"[WORKER ({self.worker_id})] "
            f"Last page before stopping\n"
            f"Car ID: {car_id}\n"
            f"URL: {url}\n"
            f"HTML length: {len(html)}\n"
            f"Page preview (first 1000 characters):\n"
            f"{html[:1000]}",
            flush=True,
        )

    def _process_url(self, car_id: int, url: str) -> dict:
        while not self._stop:
            try:
                html = self._get_valid_html(url, car_id)

                result = self.parser.parse(html)

                result["id"] = car_id
                result["url"] = url

                return result

            except CloudflareError:
                self.handle_cloudflare()

                if self._stop:
                    break

                continue

            except PageForbiddenError:
                self.handle_forbidden()
                break

            except PageNotFoundError:
                self.handle_not_found()
                break

            except InvalidPageError:
                self.handle_invalid_page()
                break

        self._reset_errors()

        return {
            "id": car_id,
            "url": url,
        }

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def _process_batch(self, batch: list[tuple[int, str]]) -> list[dict]:
        results = []

        for car_id, url in batch:
            if self._stop:
                break

            print(
                f"[WORKER ({self.worker_id})] "
                f"car id - {car_id} in processing. URL: {url}",
                flush=True,
            )

            try:
                result = self._process_url(
                    car_id,
                    url,
                )

                print(
                    f"[WORKER ({self.worker_id})] "
                    f"car id - {car_id} done",
                    flush=True,
                )

            except Exception as exc:
                print(
                    f"[WORKER ({self.worker_id})] "
                    f"Error processing car id - {car_id}: {exc}",
                    flush=True,
                )

                result = {
                    "id": car_id,
                    "url": url,
                }

            results.append(result)

        return results

    # ------------------------------------------------------------------
    # Main worker loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        print(
            f"[WORKER ({self.worker_id})] Started",
            flush=True,
        )

        try:
            while not self._stop:
                batch = self.batcher.next_batch()

                if batch is None:
                    print(
                        f"[WORKER ({self.worker_id})] "
                        f"No more cars to process",
                        flush=True,
                    )
                    break

                print(
                    f"[WORKER ({self.worker_id})] "
                    f"Reserved {len(batch)} cars",
                    flush=True,
                )

                results = self._process_batch(batch)

                self.db_writer.write(results)

                print(
                    f"[WORKER ({self.worker_id})] "
                    f"Wrote results to database",
                    flush=True,
                )

        finally:
            print(
                f"[WORKER ({self.worker_id})] "
                f"Finished and closing",
                flush=True,
            )

            self.client.close()

            print(
                f"[WORKER ({self.worker_id})] "
                f"Closed",
                flush=True,
            )

    # ------------------------------------------------------------------
    # Page error handlers
    # ------------------------------------------------------------------

    def handle_invalid_page(self) -> None:
        self._register_error("invalid_page")

    def handle_cloudflare(self) -> None:
        print(
            f"[WORKER ({self.worker_id})] "
            f"Cloudflare detected. "
            f"Waiting {self.CLOUDFLARE_TIMEOUT} seconds...",
            flush=True,
        )

        sleep(self.CLOUDFLARE_TIMEOUT)

        self._register_error("cloudflare")

    def handle_not_found(self) -> None:
        self._register_error("not_found")

    def handle_forbidden(self) -> None:
        self._register_error("forbidden")
