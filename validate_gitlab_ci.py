from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


def lint_url(api_url: str, project_id: str, ref: str) -> str:
    query = urlencode(
        {
            "content_ref": ref,
            "dry_run": "true",
            "dry_run_ref": ref,
            "include_jobs": "true",
        }
    )
    return (
        f"{api_url.rstrip('/')}/projects/{quote(project_id, safe='')}/ci/lint?{query}"
    )


def fetch_lint_result(
    api_url: str,
    project_id: str,
    ref: str,
    private_token: str,
) -> dict[str, object]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "gitlab-allure-history-ci-lint",
    }
    headers["PRIVATE-TOKEN"] = private_token

    request = Request(
        lint_url(api_url, project_id, ref),
        headers=headers,
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def validate_lint_result(result: dict[str, object]) -> None:
    errors = result.get("errors")
    if result.get("valid") is not True:
        raise RuntimeError(f"GitLab CI configuration is invalid: {errors}")

    includes = result.get("includes")
    if not isinstance(includes, list) or not includes:
        raise RuntimeError("GitLab CI Lint did not expand any includes")

    merged_yaml = result.get("merged_yaml")
    if not isinstance(merged_yaml, str) or not merged_yaml.strip():
        raise RuntimeError("GitLab CI Lint did not return merged YAML")

    jobs = result.get("jobs")
    if not isinstance(jobs, list):
        raise RuntimeError("GitLab CI Lint did not return expanded jobs")

    job_names = {
        job.get("name")
        for job in jobs
        if isinstance(job, dict) and isinstance(job.get("name"), str)
    }
    if "allure" not in job_names:
        raise RuntimeError("Expanded component configuration is missing the allure job")

    print(
        "GitLab CI configuration is valid: "
        f"{len(includes)} include(s), {len(job_names)} job(s)"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the committed pipeline and expanded component includes."
    )
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--private-token", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = fetch_lint_result(
        args.api_url,
        args.project_id,
        args.ref,
        args.private_token,
    )
    validate_lint_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
