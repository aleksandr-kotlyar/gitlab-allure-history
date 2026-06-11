from pathlib import Path

import pytest

FIXTURES_DIR = Path("tests/fixtures")
COMPONENT_INCLUDE = (
    "$CI_SERVER_FQDN/$CI_PROJECT_PATH/"
    "gitlab-allure-history@$CI_COMMIT_SHA"
)
CONTRACTS = {
    "consumer-minimal": {
        "environment": "dev",
        "pages_branch": "gl-pages",
        "has_jobid": True,
    },
    "consumer-custom-env": {
        "environment": "staging",
        "pages_branch": "gl-pages",
        "has_jobid": True,
    },
    "consumer-without-jobid": {
        "environment": "dev",
        "pages_branch": "gl-pages",
        "has_jobid": False,
    },
    "consumer-custom-pages-branch": {
        "environment": "dev",
        "pages_branch": "allure-pages",
        "has_jobid": True,
    },
}


def load_fixture(name):
    return (FIXTURES_DIR / name / ".gitlab-ci.yml").read_text(encoding="utf-8")


def test_consumer_contract_matrix_is_complete():
    fixture_names = {
        path.parent.name
        for path in FIXTURES_DIR.glob("consumer-*/.gitlab-ci.yml")
    }

    assert fixture_names == set(CONTRACTS)


@pytest.mark.parametrize("name", CONTRACTS)
def test_consumer_fixture_uses_external_component_contract(name):
    content = load_fixture(name)

    assert f"component: {COMPONENT_INCLUDE}" in content
    assert 'allure-history-image-tag: "2026.2.8"' in content
    assert "consumer_contract:" in content
    assert "allure-results" in content
    assert "verify_consumer_contract:" in content
    assert "allure:\n  rules:\n    - when: never" in content


@pytest.mark.parametrize("name, contract", CONTRACTS.items())
def test_consumer_verifies_expanded_component_inputs(name, contract):
    content = load_fixture(name)

    assert f'test "$ENV" = "{contract["environment"]}"' in content
    assert f'test "$PAGES_BRANCH" = "{contract["pages_branch"]}"' in content


def test_custom_consumers_set_inputs_through_component_api():
    minimal = load_fixture("consumer-minimal")
    custom_env = load_fixture("consumer-custom-env")
    custom_pages = load_fixture("consumer-custom-pages-branch")

    assert "environment:" not in minimal
    assert "pages-branch:" not in minimal
    assert "environment: staging" in custom_env
    assert "pages-branch: allure-pages" in custom_pages


@pytest.mark.parametrize("name, contract", CONTRACTS.items())
def test_consumer_jobid_artifact_matrix(name, contract):
    content = load_fixture(name)
    has_jobid_artifact = "\n      - jobid\n" in content

    assert has_jobid_artifact is contract["has_jobid"]


def test_without_jobid_consumer_omits_jobid_artifact():
    content = load_fixture("consumer-without-jobid")

    assert '> jobid' not in content
    assert "\n      - jobid\n" not in content
    assert "test ! -e jobid" in content


def test_project_pipeline_executes_every_consumer_as_a_child_pipeline():
    pipeline = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    for name in CONTRACTS:
        assert f"consumer_contract:{name.removeprefix('consumer-')}:" in pipeline
        assert f"local: tests/fixtures/{name}/.gitlab-ci.yml" in pipeline

    assert pipeline.count("strategy: mirror") == len(CONTRACTS)
