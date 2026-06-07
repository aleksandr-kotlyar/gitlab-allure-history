import json
import textwrap
from pathlib import Path


def extract_python_heredoc(template: str, marker: str) -> str:
    lines = template.splitlines()
    start = lines.index(marker) + 1
    end = lines.index("      PY", start)

    return textwrap.dedent("\n".join(lines[start:end]))


def test_executor_report_url_points_to_report_snapshot(tmp_path, monkeypatch):
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")
    script = extract_python_heredoc(template, "      python3 - <<'PY'")

    monkeypatch.chdir(tmp_path)
    (tmp_path / "allure-results").mkdir()

    monkeypatch.setenv("CI_PAGES_URL", "https://example.gitlab.io/project/")
    monkeypatch.setenv("REPORT_ENV", "dev")
    monkeypatch.setenv("REPORT_BRANCH", "feature-login")
    monkeypatch.setenv("REPORT_DIR", "job_123")
    monkeypatch.setenv("CI_PIPELINE_URL", "https://gitlab.example/pipeline/1")
    monkeypatch.setenv("JOB_ID", "123")

    exec(script, {"__builtins__": __builtins__})

    executor = json.loads((tmp_path / "allure-results" / "executor.json").read_text())

    assert executor["reportUrl"] == "https://example.gitlab.io/project/dev/feature-login/job_123/"


def test_project_pipeline_dogfoods_reusable_template():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    assert "include:\n  - local: templates/gitlab-allure-history.yml" in pipeline


def test_template_uses_url_safe_branch_slug_and_defined_image_tag():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert "IMAGE_TAG: $CI_COMMIT_REF_SLUG" in template
    assert "ALLURE_HISTORY_IMAGE: $CI_COMMIT_REF_SLUG" not in template
    assert "REPORT_BRANCH=\"${CI_COMMIT_REF_SLUG:-detached}\"" in template
    assert "CI_COMMIT_REF_NAME" not in template


def test_template_does_not_use_component_inputs():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert "spec:" not in template
    assert "inputs:" not in template


def test_readme_external_include_uses_pinned_ref_placeholder():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "project: aleksandr-kotlyar/gitlab-allure-history" in readme
    assert "ref: <pinned-tag-or-commit-sha>" in readme
