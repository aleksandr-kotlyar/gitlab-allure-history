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
