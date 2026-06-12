import json
import subprocess
import textwrap
from pathlib import Path


def extract_python_heredoc(template: str, marker: str) -> str:
    lines = template.splitlines()
    start = lines.index(marker) + 1
    end = lines.index("      PY", start)

    return textwrap.dedent("\n".join(lines[start:end]))


def extract_mr_note_lookup_python(template: str) -> str:
    start_marker = "      MATCH_INFO=$(printf '%s' \"${NOTES_JSON}\" | python3 -c '"
    start = template.index(start_marker) + len(start_marker)
    end = template.index("      ' \"${CURRENT_USER_ID}\"", start)

    return textwrap.dedent(template[start:end])


def extract_mr_comment_python(template: str) -> str:
    start_marker = "      COMMENT_BODY=$(python3 <<'PY'"
    lines = template.splitlines()
    start = lines.index(start_marker) + 1
    end = lines.index("      PY", start)

    return textwrap.dedent("\n".join(lines[start:end]))


def render_mr_comment(tmp_path, monkeypatch, statistic):
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")
    script = extract_mr_comment_python(template)
    report_dir = tmp_path / "job_123"
    widgets_dir = report_dir / "widgets"
    widgets_dir.mkdir(parents=True)
    (widgets_dir / "summary.json").write_text(
        json.dumps({"statistic": statistic}),
        encoding="utf-8",
    )
    monkeypatch.setenv("REPORT_DIR", str(report_dir))
    monkeypatch.setenv("REPORT_URL", "https://example.gitlab.io/project/dev/branch/job_123/")

    result = subprocess.run(
        ["python3", "-c", script],
        text=True,
        capture_output=True,
        check=True,
    )

    return result.stdout.rstrip("\n")


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
    assert 'allure-history-image-tag: "2026.2.8"' in pipeline
    assert "if: $CI_COMMIT_TAG == null" in pipeline
    assert "GITLAB_ALLURE_HISTORY_VERSION:" not in pipeline
    assert "build_python:\n  tags:\n    - macos-local" in pipeline
    assert "create_release:" in pipeline
    assert "tag_name: $CI_COMMIT_TAG" in pipeline


def test_project_pipeline_validates_expanded_component_with_ci_lint_api():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "ci_lint:\n  stage: test\n" in pipeline
    assert '    - test -n "${ALLURE_HISTORY_TOKEN:-}"' in pipeline
    assert "    - python3 validate_gitlab_ci.py" in pipeline
    assert '        --api-url "$CI_API_V4_URL"' in pipeline
    assert '        --project-id "$CI_PROJECT_ID"' in pipeline
    assert '        --ref "$CI_COMMIT_REF_NAME"' in pipeline
    assert '        --private-token "$ALLURE_HISTORY_TOKEN"' in pipeline
    assert "reuses the masked `ALLURE_HISTORY_TOKEN` with `api`" in readme


def test_project_pipeline_smokes_published_pages_after_allure():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    assert "pages_smoke:\n  stage: release\n" in pipeline
    assert "    - job: test_gate\n      artifacts: true" in pipeline
    assert "    - job: allure\n      artifacts: false" in pipeline
    assert '        --base-url "$CI_PAGES_URL"' in pipeline
    assert '        --environment "$ENV"' in pipeline
    assert '        --branch "$CI_COMMIT_REF_SLUG"' in pipeline
    assert '        --report "job_$(cat jobid)"' in pipeline


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
    assert "  component: [version, reference]\n" in template
    assert "  inputs:\n" in template
    assert "    environment:\n" in template
    assert "    allure-history-image:\n" in template
    assert "    allure-history-image-tag:\n" in template
    assert "    pages-branch:\n" in template
    assert "    reports-to-keep:\n" in template
    assert "    build-runtime-image:\n" in template
    assert "---\n\nvariables:" in template


def run_mr_note_lookup(body):
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")
    script = extract_mr_note_lookup_python(template)
    notes = [
        {
            "id": 123,
            "body": body,
            "system": False,
            "author": {"id": 42},
        }
    ]

    result = subprocess.run(
        ["python3", "-c", script, "42"],
        input=json.dumps(notes),
        text=True,
        capture_output=True,
        check=True,
    )

    return result.stdout.strip()


def test_mr_note_lookup_finds_allure_report_link():
    assert run_mr_note_lookup(
        "> [!tip]\n"
        "> \U0001f7e2 **PASSED** \u00b7 [Allure report](https://example.test/#categories)"
    ) == "OWN:123"


def test_mr_note_lookup_keeps_legacy_marker_compatibility():
    assert run_mr_note_lookup(
        "Allure report\n\n<!-- allure-history-report -->"
    ) == "OWN:123"


def test_failed_mr_comment_uses_caution_alert(tmp_path, monkeypatch):
    comment = render_mr_comment(
        tmp_path,
        monkeypatch,
        {"passed": 42, "failed": 1, "broken": 1, "skipped": 0, "unknown": 0, "total": 44},
    )

    assert comment == (
        "> [!caution]\n"
        "> \U0001f534 **FAILED** \u00b7 "
        "[Allure report 2 issues]"
        "(https://example.gitlab.io/project/dev/branch/job_123/#categories) "
        "(failed 1, broken 1) \u00b7 44 total"
    )


def test_passed_mr_comment_uses_tip_alert(tmp_path, monkeypatch):
    comment = render_mr_comment(
        tmp_path,
        monkeypatch,
        {"passed": 44, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0, "total": 44},
    )

    assert comment == (
        "> [!tip]\n"
        "> \U0001f7e2 **PASSED** \u00b7 "
        "[Allure report]"
        "(https://example.gitlab.io/project/dev/branch/job_123/#categories) "
        "\u00b7 44 total"
    )


def test_readme_external_include_uses_pinned_component_version():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert (
        "component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/"
        "gitlab-allure-history@2026.2.7"
        in readme
    )
    assert "allure-history-image-tag: 2026.2.7" in readme
    assert "Never use moving references (branches, `~latest`)" in readme
