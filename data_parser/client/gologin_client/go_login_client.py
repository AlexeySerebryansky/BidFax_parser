import os
import shutil
import subprocess
from time import sleep

from dotenv import load_dotenv

load_dotenv()


class GoLoginClient:
    MAX_OPEN_RETRIES = 3
    MAX_CHECK_RETRIES = 3

    OPEN_TIMEOUT = 30
    COMMAND_TIMEOUT = 30
    CHECK_DELAY = 5

    MIN_LEN_HTML = 10000

    GOLOGIN_CLI = shutil.which("gologin-agent-browser")

    if not GOLOGIN_CLI:
        raise RuntimeError(
            "gologin--agent-browser not found"
        )

    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.profile_id = self._get_profile_id()

        self.session_id = f"worker-{worker_id}"

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

    def _run(self, *args: str, timeout: int = COMMAND_TIMEOUT) -> str:
        command = [
            self.GOLOGIN_CLI,
            "local",
            *args,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout
            )
        except subprocess.TimeoutExpired:
            print(
                f"[GOLOGIN ({self.profile_id})] "
                f"TIMEOUT after {timeout}s: {' '.join(command)}",
                flush=True,
            )
            raise

        if result.returncode != 0:
            raise RuntimeError(
                f"GoLogin CLI error:\n{result.stderr}"
            )

        return result.stdout

    def _run_close(self) -> None:
        command = [
            self.GOLOGIN_CLI,
            "local",
            "close",
            "--session",
            self.session_id,
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            process.wait(timeout=10)

        except subprocess.TimeoutExpired:
            print(
                f"[GOLOGIN ({self.profile_id})] "
                f"Close command timeout",
                flush=True,
            )

            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )

            raise

    def _kill_profile_browser(self):
        """
        Forcefully terminates the Orbita browser process belonging
        to this GoLogin profile.

        This is a fallback for cases when the normal GoLogin
        `close --session` command hangs or fails.
        """

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-CimInstance Win32_Process | "
                        "Where-Object { "
                        "$_.Name -eq 'chrome.exe' -and "
                        "$_.ExecutablePath -like '*orbita-browser-150*' -and "
                        "$_.CommandLine -like '*"
                        f"{self.profile_id}"
                        "*' "
                        "} | "
                        "Select-Object ProcessId, ParentProcessId, CommandLine | "
                        "ConvertTo-Json -Compress"
                    ),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )

            if result.returncode != 0:
                print(
                    f"[GOLOGIN - Worker ({self.worker_id})] "
                    f"Failed to query Orbita processes: {result.stderr.strip()}",
                    flush=True,
                )
                return

            output = result.stdout.strip()

            if not output:
                print(
                    f"[GOLOGIN - Worker ({self.worker_id})] "
                    f"No Orbita process found for profile",
                    flush=True,
                )
                return

            import json

            processes = json.loads(output)

            if isinstance(processes, dict):
                processes = [processes]

            if not processes:
                print(
                    f"[GOLOGIN - Worker ({self.worker_id})] "
                    f"No Orbita process found for profile",
                    flush=True,
                )
                return

            # The main Orbita process is the one whose parent
            # is not another Orbita process.
            orbita_pids = {
                int(process["ProcessId"])
                for process in processes
            }

            main_process = None

            for process in processes:
                parent_pid = int(process["ParentProcessId"])

                if parent_pid not in orbita_pids:
                    main_process = process
                    break

            if main_process is None:
                main_process = processes[0]

            pid = int(main_process["ProcessId"])

            kill_result = subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(pid),
                    "/T",
                    "/F",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )

            if kill_result.returncode == 0:
                print(
                    f"[GOLOGIN - Worker ({self.worker_id})] "
                    f"Orbita process tree terminated",
                    flush=True,
                )
            else:
                print(
                    f"[GOLOGIN - Worker ({self.worker_id})] "
                    f"Failed to terminate Orbita: "
                    f"{kill_result.stderr.strip() or kill_result.stdout.strip()}",
                    flush=True,
                )

        except subprocess.TimeoutExpired:
            print(
                f"[GOLOGIN - Worker ({self.worker_id})] "
                f"Process cleanup timed out",
                flush=True,
            )

        except Exception as e:
            print(
                f"[GOLOGIN - Worker ({self.worker_id})] "
                f"Process cleanup failed: {e}",
                flush=True,
            )

    def get_html(self, url: str) -> str:
        for open_attempt in range(1, self.MAX_OPEN_RETRIES + 1):

            try:
                self._run(
                    "open",
                    url,
                    "--profile",
                    self.profile_id,
                    "--session",
                    self.session_id,
                    "--background",
                    timeout=self.OPEN_TIMEOUT,
                )

            except subprocess.TimeoutExpired:
                print(
                    f"[GOLOGIN ({self.profile_id})] "
                    f"OPEN timeout",
                    flush=True,
                )
                continue

            for check_attempt in range(1, self.MAX_CHECK_RETRIES + 1):

                try:
                    title = self._run(
                        "get",
                        "title",
                        "--session",
                        self.session_id,
                        timeout=self.COMMAND_TIMEOUT,
                    ).strip()

                    if self._is_cloudflare(title):
                        print(
                            f"[GOLOGIN ({self.profile_id})] "
                            f"Cloudflare detected",
                            flush=True,
                        )

                        sleep(self.CHECK_DELAY)
                        continue

                    html = self._run(
                        "get",
                        "html",
                        "--session",
                        self.session_id,
                        timeout=self.COMMAND_TIMEOUT,
                    )

                    if len(html) >= self.MIN_LEN_HTML:
                        return html

                    print(
                        f"[GOLOGIN - Worker ({self.worker_id})] "
                        f"HTML is too small, retrying {check_attempt}/3",
                        flush=True,
                    )

                except subprocess.TimeoutExpired:
                    print(
                        f"[GOLOGIN ({self.profile_id})] "
                        f"GET timeout, reopening page",
                        flush=True,
                    )
                    break

                sleep(self.CHECK_DELAY)
        raise TimeoutError(
            f"BidFax did not finish loading: {url}"
        )

    def close(self):

        try:
            self._run_close()

            print(
                f"[GOLOGIN ({self.profile_id})] Session closed normally",
                flush=True,
            )

        except Exception:
            print(
                f"[GOLOGIN ({self.profile_id})] Normal close failed",
                "Starting killing process",
                flush=True,
            )


            self._kill_profile_browser()


        finally:
            print(
                f"[GOLOGIN ({self.session_id})] "
                f"Session {self.worker_id} closed",
                flush=True,
            )