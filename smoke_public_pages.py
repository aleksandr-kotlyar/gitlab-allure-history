from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_ATTEMPTS = 12
DEFAULT_DELAY_SECONDS = 5.0
USER_AGENT = "gitlab-allure-history-pages-smoke"


def public_page_urls(base_url: str, environment: str, branch: str, report: str):
    base_url = base_url.rstrip("/")
    path_parts = [quote(part, safe="") for part in (environment, branch)]
    environment_url = f"{base_url}/{path_parts[0]}/"
    branch_url = f"{environment_url}{path_parts[1]}/"

    return (
        environment_url,
        branch_url,
        f"{branch_url}latest/",
        f"{branch_url}{quote(report, safe='')}/",
    )


def fetch_page(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=15) as response:
        status = response.status
        final_url = response.geturl()
        response.read(1)

    return status, final_url


def wait_for_public_pages(
    urls: tuple[str, ...],
    attempts: int = DEFAULT_ATTEMPTS,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    fetch: Callable[[str], tuple[int, str]] = fetch_page,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    failures = {}

    for attempt in range(1, attempts + 1):
        failures = {}

        for url in urls:
            try:
                status, final_url = fetch(url)
                if not 200 <= status < 300:
                    failures[url] = f"HTTP {status}"
                else:
                    print(f"OK {url} -> {final_url} ({status})")
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                failures[url] = str(error)

        if not failures:
            return

        details = "; ".join(f"{url}: {error}" for url, error in failures.items())
        print(f"Attempt {attempt}/{attempts} failed: {details}", file=sys.stderr)

        if attempt < attempts:
            sleep(delay_seconds)

    raise RuntimeError(
        "Public Pages smoke failed: "
        + "; ".join(f"{url}: {error}" for url, error in failures.items())
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify published GitLab Pages navigation and report URLs."
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--attempts", type=int, default=DEFAULT_ATTEMPTS)
    parser.add_argument("--delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.attempts < 1 or args.delay_seconds < 0:
        raise SystemExit("--attempts must be positive and --delay-seconds non-negative")

    urls = public_page_urls(
        args.base_url,
        args.environment,
        args.branch,
        args.report,
    )
    wait_for_public_pages(
        urls,
        attempts=args.attempts,
        delay_seconds=args.delay_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
