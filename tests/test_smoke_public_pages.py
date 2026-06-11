from urllib.error import HTTPError

import pytest

from smoke_public_pages import public_page_urls, wait_for_public_pages


def test_public_page_urls_cover_environment_branch_latest_and_fresh_report():
    assert public_page_urls(
        "https://example.gitlab.io/project/",
        "dev",
        "feature login",
        "job_123",
    ) == (
        "https://example.gitlab.io/project/dev/",
        "https://example.gitlab.io/project/dev/feature%20login/",
        "https://example.gitlab.io/project/dev/feature%20login/latest/",
        "https://example.gitlab.io/project/dev/feature%20login/job_123/",
    )


def test_wait_for_public_pages_retries_until_every_url_is_available():
    urls = ("https://example.test/dev/", "https://example.test/dev/master/latest/")
    calls = []
    sleeps = []

    def fetch(url):
        calls.append(url)
        if len(calls) <= len(urls):
            raise HTTPError(url, 404, "Not Found", {}, None)
        return 200, url

    wait_for_public_pages(
        urls,
        attempts=2,
        delay_seconds=3,
        fetch=fetch,
        sleep=sleeps.append,
    )

    assert calls == [*urls, *urls]
    assert sleeps == [3]


def test_wait_for_public_pages_reports_unavailable_urls():
    url = "https://example.test/dev/master/job_123/"

    with pytest.raises(RuntimeError, match="job_123"):
        wait_for_public_pages(
            (url,),
            attempts=1,
            delay_seconds=0,
            fetch=lambda requested_url: (503, requested_url),
        )
