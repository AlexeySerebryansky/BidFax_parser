from bs4 import BeautifulSoup


class PageValidator:
    SHORT_STORY_SELECTOR = "p.short-story, p.short-story2"
    PHOTOS_SELECTOR = "..."

    @classmethod
    def is_valid(cls, html: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")

        has_short_story = soup.select_one(
            cls.SHORT_STORY_SELECTOR
        ) is not None

        has_photos = soup.find(
            "img",
            src=lambda src: src and "/uploads/" in src,
        ) is not None

        return has_short_story and has_photos
