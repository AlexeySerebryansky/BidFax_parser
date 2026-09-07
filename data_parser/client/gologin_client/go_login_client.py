import os
import shutil
import subprocess
from time import sleep

from dotenv import load_dotenv

load_dotenv()


class GoLoginClient:
    GOLOGIN_CLI = shutil.which("gologin-agent-browser")

    if not GOLOGIN_CLI:
        raise RuntimeError(
            "gologin--agent-browser not found"
        )

    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.profile_id = self._get_profile_id()


    def _get_profile_id(self) -> str:
        env_name = (
            f"GOLOGIN_PROFILE_{self.worker_id}"
        )

        profile_id = os.getenv(env_name)

        if not profile_id:
            raise RuntimeError(
                f"{env_name} is not set"
            )

        return profile_id

    def _run(self, *args: str) -> str:
        command = [
            self.GOLOGIN_CLI,
            "local",
            *args,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"GoLogin CLI error:\n{result.stderr}"
            )

        return result.stdout

    def get_html(self, url: str) -> str:

        self._run(
            "open",
            url,
            "--profile",
            self.profile_id,
            "--background"
        )

        for attempt in range(3):
            title = self._run(
                "get",
                "title"
            ).strip()

            if not self._is_cloudflare(title):
                html = self._run("get", "html")

                if len(html) >= 10_000:
                    return html

            sleep(5)

        raise TimeoutError(
            "BidFax did not finish loading"
        )

    def close(self):
        self._run("close")

    @staticmethod
    def _is_cloudflare(title: str) -> bool:
        markers = (
            "Just a moment",
            "Checking your browser",
            "Verify you are human"
        )

        return any(
            marker.lower() in title.lower()
            for marker in markers
        )
