from pathlib import Path


def test_template_delegates_publish_flow_to_core_gitlab_helper():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert "image: registry.gitlab.com/aleksandr-kotlyar/allure-history-core:2026.2.11" in template
    assert "allure-history-gitlab publish-job" in template
    assert "allure-history build-report" not in template
    assert "git ls-remote" not in template
    assert "/merge_requests/" not in template


def test_project_pipeline_dogfoods_reusable_template():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    assert (
        "include:\n"
        "  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_TAG"
        in pipeline
    )
    assert "  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_SHA" in pipeline
    assert "if: $CI_COMMIT_TAG == null" in pipeline
    assert (
        'GIT_CLONE_PATH: "$CI_BUILDS_DIR/$CI_PROJECT_PATH_SLUG/$CI_CONCURRENT_PROJECT_ID"'
        in pipeline
    )
    assert "allure-history-image-tag:" not in pipeline
    assert "GITLAB_ALLURE_HISTORY_VERSION:" not in pipeline
    assert "create_release:" in pipeline
    assert "tag_name: $CI_COMMIT_TAG" in pipeline


def test_project_pipeline_validates_expanded_component_with_ci_lint_api():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "ci_lint:\n  stage: test\n" in pipeline
    assert '    - test -n "${ALLURE_HISTORY_TOKEN:-}"' in pipeline
    assert "    - python3 validate_gitlab_ci.py" in pipeline
    assert '        --api-url "$CI_API_V4_URL"' in pipeline
    assert '        --project-id "$CI_PROJECT_ID"' in pipeline
    assert '        --ref "$CI_COMMIT_SHA"' in pipeline
    assert '        --private-token "$ALLURE_HISTORY_TOKEN"' in pipeline
    assert "`ci_lint` calls `validate_gitlab_ci.py` with the GitLab CI Lint API" in contributing
    assert "requires `ALLURE_HISTORY_TOKEN` with `api` scope" in contributing


def test_project_pipeline_smokes_published_pages_after_publish_job():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")
    publish_job = pipeline.split("\npublish-allure-history:\n", 1)[1].split(
        "\npages_smoke:\n", 1
    )[0]
    pages_smoke_job = pipeline.split("\npages_smoke:\n", 1)[1].split(
        "\ncreate_release:\n", 1
    )[0]

    assert "  dependencies:\n    - test_gate\n    - test_demo" in publish_job
    assert "pages_smoke:\n  stage: release\n" in pipeline
    assert "  image: registry.gitlab.com/aleksandr-kotlyar/allure-history-core:2026.2.11" in pages_smoke_job
    assert "    - job: test_gate\n      artifacts: true" in pages_smoke_job
    assert "    - job: publish-allure-history\n      artifacts: false" in pages_smoke_job
    assert '        --base-url "$CI_PAGES_URL"' in pages_smoke_job
    assert '        --environment "$ENV"' in pages_smoke_job
    assert '        --branch "$CI_COMMIT_REF_SLUG"' in pages_smoke_job
    assert "    - test -s jobid" in pages_smoke_job
    assert '        --report "job_$(cat jobid)"' in pages_smoke_job


def test_project_pipeline_uses_job_specific_images():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    assert "default:\n  image: python:3.14\n" in pipeline
    assert "pages_smoke:\n  stage: release\n  image: registry.gitlab.com/aleksandr-kotlyar/allure-history-core:2026.2.11\n" in pipeline
    assert "create_release:\n  stage: release\n  image: registry.gitlab.com/gitlab-org/cli:latest\n" in pipeline


def test_template_defines_component_inputs():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")

    assert template.startswith("spec:\n")
    assert "  component: [version, reference]\n" in template
    assert "  inputs:\n" in template
    assert "    environment:\n" in template
    assert "    pages-branch:\n" in template
    assert "    reports-to-keep:\n" in template
    assert "    comment-mr:\n" in template
    assert "allure-history-image" not in template
    assert "allure-history-image-tag" not in template
    assert "allure-history-tools-dir" not in template
    assert "build-runtime-image" not in template
    assert "---\n\nvariables:" in template


def test_publish_job_publishes_public_as_gitlab_pages_artifact():
    template = Path("templates/gitlab-allure-history.yml").read_text(encoding="utf-8")
    publish_job = template.split("\npublish-allure-history:\n", 1)[1]

    assert "\n  pages: true\n" in publish_job
    assert (
        "  artifacts:\n"
        "    when: always\n"
        "    expire_in: 1 week\n"
        "    paths:\n"
        "      - public\n"
    ) in publish_job


def test_readme_external_include_uses_pinned_component_version():
    readme = Path("README.md").read_text(encoding="utf-8")
    usage_docs = readme.split("## Component Inputs", 1)[0]

    assert (
        "component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/"
        "gitlab-allure-history@2026.2.11"
        in readme
    )
    assert "allure-history-image-tag:" not in usage_docs
    assert "allure-history-image-tag" not in readme
    assert "pin a published release tag" in readme
