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

    assert (
        "include:\n"
        "  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_TAG"
        in pipeline
    )
    assert "allure-history-image-tag: $CI_COMMIT_TAG" in pipeline
    assert 'build-runtime-image: "true"' in pipeline
    assert "  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_SHA" in pipeline
    assert 'allure-history-image-tag: "2026.2.1"' in pipeline
    assert "if: $CI_COMMIT_TAG == null" in pipeline
    assert "create_release:" in pipeline
    assert "tag_name: $CI_COMMIT_TAG" in pipeline


def test_template_uses_url_safe_branch_slug_and_component_versioned_image_tag():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert '"$[[ inputs.build-runtime-image ]]" == "true" && $CI_COMMIT_TAG' in template
    assert "IMAGE_TAG: $CI_COMMIT_TAG" in template
    assert (
        "ALLURE_HISTORY_IMAGE: $[[ inputs.allure-history-image ]]:$[[ inputs.allure-history-image-tag ]]"
        in template
    )
    assert "docker build -t \"$CI_REGISTRY_IMAGE:$IMAGE_TAG\" ." in template
    assert "docker push \"$CI_REGISTRY_IMAGE:$IMAGE_TAG\"" in template
    assert "docker tag \"$CI_REGISTRY_IMAGE:$IMAGE_TAG\"" not in template
    assert "IMAGE_TAG: $CI_COMMIT_SHA" not in template
    assert "ALLURE_HISTORY_IMAGE: $[[ inputs.allure-history-image ]]:$[[ component.version ]]" not in template
    assert "ALLURE_HISTORY_IMAGE: $CI_COMMIT_REF_SLUG" not in template
    assert "REPORT_BRANCH=\"${CI_COMMIT_REF_SLUG:-detached}\"" in template
    assert "CI_COMMIT_REF_NAME" not in template


def test_template_defines_component_inputs():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert template.startswith("spec:\n")
    assert "  component: [version]\n" not in template
    assert "  inputs:\n" in template
    assert "    environment:\n" in template
    assert "    allure-history-image:\n" in template
    assert "    allure-history-image-tag:\n" in template
    assert "    pages-branch:\n" in template
    assert "    reports-to-keep:\n" in template
    assert "    build-runtime-image:\n" in template
    assert "---\n\nvariables:" in template


def test_readme_external_include_uses_pinned_component_version():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert (
        "component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/"
        "gitlab-allure-history@<pinned-version-tag>"
        in readme
    )
    assert "allure-history-image-tag: <pinned-version-tag>" in readme
    assert "Avoid moving references such as branches or `~latest`" in readme
