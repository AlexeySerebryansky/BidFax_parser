from bs4 import BeautifulSoup


class PageValidationError(Exception):
    """Base exception for page validation errors."""


class PageForbiddenError(PageValidationError):
    """403 Forbidden."""


class PageNotFoundError(PageValidationError):
    """404 Not Found."""


class CloudflareError(PageValidationError):
    """Cloudflare challenge/protection detected."""


class InvalidPageError(PageValidationError):
    """Page structure is not valid."""


class PageValidator:
    SHORT_STORY_SELECTOR = "p.short-story, p.short-story2"

    CLOUDFLARE_MARKERS = (
        "just a moment",
        "checking your browser",
        "verify you are human",
        "cf-chl-",
        "challenge-platform",
        "cloudflare ray id",
        "attention required! | cloudflare",
        "enable javascript and cookies to continue",
    )

    FORBIDDEN_MARKERS = (
        "403 forbidden",
        "error 403",
    )

    NOT_FOUND_MARKERS = (
        "404 not found",
        "error 404",
        "page not found",
    )

    @classmethod
    def validate(cls, html: str) -> str:
        cls._validate_input(html)

        if cls._is_cloudflare(html):
            raise CloudflareError(
                "Cloudflare protection page detected"
            )
        if cls._is_403(html):
            raise PageForbiddenError(
                "403 Forbidden: access to the page was denied"
            )

        if cls._is_404(html):
            raise PageNotFoundError(
                "404 Not Found: page does not exist"
            )

        if not cls._is_valid_structure(html):
            raise InvalidPageError(
                "Page does not contain expected lot structure"
            )

        return html

    @staticmethod
    def _validate_input(html: str) -> None:
        if not isinstance(html, str):
            raise PageValidationError(
                f"Expected HTML as str, got {type(html).__name__}"
            )

        if not html.strip():
            raise PageValidationError(
                "Received empty HTML"
            )

    @classmethod
    def _is_valid_structure(cls, html: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")

        has_short_story = soup.select_one(
            cls.SHORT_STORY_SELECTOR
        ) is not None

        has_photos = soup.find(
            "img",
            src=lambda src: src and "/uploads/" in src,
        ) is not None

        return has_short_story and has_photos

    @classmethod
    def _is_403(cls, html: str) -> bool:
        html_lower = html.lower()

        return any(
            marker.lower() in html_lower
            for marker in cls.FORBIDDEN_MARKERS
        )

    @classmethod
    def _is_404(cls, html: str) -> bool:
        html_lower = html.lower()

        return any(
            marker.lower() in html_lower
            for marker in cls.NOT_FOUND_MARKERS
        )

    @classmethod
    def _is_cloudflare(cls, html: str) -> bool:
        html_lower = html.lower()

        return any(
            marker.lower() in html_lower
            for marker in cls.CLOUDFLARE_MARKERS
        )