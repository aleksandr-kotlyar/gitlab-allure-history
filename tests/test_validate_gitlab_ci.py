import json

import pytest

import validate_gitlab_ci
from validate_gitlab_ci import fetch_lint_result, lint_url, validate_lint_result


def valid_lint_result():
    return {
        "valid": True,
        "errors": [],
        "warnings": [],
        "merged_yaml": "publish-allure-history:\n  script:\n    - echo report\n",
        "includes": [{"type": "component", "location": "component.yml"}],
        "jobs": [{"name": "test_gate"}, {"name": "publish-allure-history"}],
    }


def test_lint_url_requests_static_validation_for_current_ref():
    url = lint_url(
        "https://gitlab.example/api/v4/",
        "group/project",
        "feature/ci-lint",
    )

    assert url.startswith(
        "https://gitlab.example/api/v4/projects/group%2Fproject/ci/lint?"
    )
    assert "content_ref=feature%2Fci-lint" in url
    assert "include_jobs=true" in url
    assert "dry_run" not in url


def test_validate_lint_result_accepts_expanded_component_pipeline():
    validate_lint_result(valid_lint_result())


def test_fetch_lint_result_uses_optional_private_token(monkeypatch):
    captured_request = None

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return json.dumps(valid_lint_result()).encode()

    def open_request(request, timeout):
        nonlocal captured_request
        captured_request = request
        assert timeout == 30
        return Response()

    monkeypatch.setattr(validate_gitlab_ci, "urlopen", open_request)

    result = fetch_lint_result(
        "https://gitlab.example/api/v4",
        "123",
        "abc123",
        private_token="secret",
    )

    assert result["valid"] is True
    assert captured_request.get_header("Private-token") == "secret"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("valid", False, "configuration is invalid"),
        ("includes", [], "did not expand any includes"),
        ("merged_yaml", "", "did not return merged YAML"),
        ("jobs", [], "missing the publish-allure-history job"),
    ],
)
def test_validate_lint_result_rejects_incomplete_validation(field, value, message):
    result = valid_lint_result()
    result[field] = value

    with pytest.raises(RuntimeError, match=message):
        validate_lint_result(result)
