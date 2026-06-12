# Contributing

Thanks for your interest in improving `gitlab-allure-history`.

This project is a lightweight GitLab CI component for publishing branch-based Allure report history to GitLab Pages.

The main goal is to stay small, static, and GitLab-native.

## Scope and non-goals

In scope:

* GitLab CI/CD component usability;
* static GitLab Pages report publishing;
* immutable report snapshots;
* stable branch-level `latest/` aliases;
* safe pruning;
* generated index navigation;
* merge request report links;
* clear diagnostics for common GitLab CI integration issues.

Non-goals:

* a ReportPortal replacement;
* a test management system;
* a backend dashboard;
* database-backed analytics;
* generic multi-CI publishing;
* object storage archival;
* a custom Allure renderer.

Operational constraints:

* report history requires a writable Pages storage branch;
* publishing is serialized with a `resource_group` and retries raced pushes up to three times;
* different branch names can theoretically normalize to the same `CI_COMMIT_REF_SLUG`;
* report retention defaults to 30 snapshots per environment and branch.

## Development Requirements

* Python and `pip`;
* dependencies from `requirements.txt`;
* GitLab CI/CD for full pipeline validation;
* GitLab Pages and a writable Pages branch for publishing checks;
* `GIT_PUSH_TOKEN` with `write_repository` permission for Pages publishing;
* `ALLURE_HISTORY_TOKEN` with `api` scope for CI lint and MR comment checks.

## Running tests

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the full suite:

```bash
pytest
```

Run the blocking local gate:

```bash
pytest -m "not demo"
```

Optionally run demo tests:

```bash
pytest -m "demo"
```

Demo tests may intentionally produce failed, broken, or skipped Allure states. They generate meaningful non-green example reports and are not a blocking gate.

Focused examples:

```bash
pytest tests/test_generate_index.py
pytest tests/test_prune_reports.py
pytest tests/test_gitlab_template.py
```

To test index generation directly:

```bash
python3 generate_index.py public
```

## How This Repository Uses Itself

The project includes its own component from `.gitlab-ci.yml`. Tag pipelines build and use the matching release image. Non-tag pipelines include the component at the current commit SHA and use the latest published fallback image:

```yaml
include:
  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_TAG
    inputs:
      allure-history-image-tag: $CI_COMMIT_TAG
      build-runtime-image: "true"
    rules:
      - if: $CI_COMMIT_TAG
  - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/gitlab-allure-history@$CI_COMMIT_SHA
    inputs:
      allure-history-image-tag: "2026.2.8"
    rules:
      - if: $CI_COMMIT_TAG == null
```

After each release, update the fallback image tag in `.gitlab-ci.yml`.

## CI-only Validation

These checks require GitLab CI context and variables; they are not normal local-only checks:

* `ci_lint` calls `validate_gitlab_ci.py` with the GitLab CI Lint API. It validates the current commit and checks that the component include expands to the expected `publish-allure-history` job. It requires `ALLURE_HISTORY_TOKEN` with `api` scope.
* `consumer_contract:*` executes each `tests/fixtures/consumer-*` configuration as a child pipeline against the component at the current commit SHA. Fixtures disable publishing and verify expanded inputs and upstream artifacts without modifying Pages content.
* `pages_smoke` validates the published root, branch index, `latest/` alias, and immutable report URL.

## Key Files

| File | Purpose |
|------|---------|
| `.gitlab-ci.yml` | Dogfooding, CI lint, consumer contracts, Pages smoke checks, and release jobs. |
| `templates/gitlab-allure-history.yml` | Reusable GitLab CI component. |
| `tests/fixtures/consumer-*` | External consumer configurations executed as child pipelines. |
| `validate_gitlab_ci.py` | GitLab CI Lint API validation. |
| `Dockerfile` | Runtime image with Python, Java, Git, and Allure CLI. |
| `generate_index.py` | Static HTML index generator. |
| `prune_reports.py` | Report snapshot retention. |
| `smoke_public_pages.py` | Published Pages smoke checks. |
| `pytest.ini` | Pytest markers and Allure configuration. |
| `tests/` | Gate, component, and demo tests. |
| `CHANGELOG.md` | Release history and policy. |

## Testing generated indexes

The generated index pages are part of the product.

When changing `generate_index.py`, check that:

* the root index opens;
* the environment index opens;
* the branch index opens;
* immutable `job_NNN/` report links still work;
* `latest/` redirects to the newest immutable report;
* issue summary links point to Allure categories;
* `latest/` is not listed as a regular report snapshot;
* hidden and internal folders remain excluded;
* light and dark themes still work if affected.

Important internal entries must not appear as normal rows:

```text
history/
latest/
index.html
.modified_at
```

Expected branch report layout:

```text
public/
  dev/
    master/
      index.html
      latest/
        index.html
      history/
      job_NNN/
      job_NNN/
```

`latest/` must be a lightweight redirect alias to the newest immutable `job_NNN/` report. It must not copy the full report.

## Testing Latest Report Aliases

When changing latest report logic, verify:

* `latest/index.html` is generated for folders containing report snapshots;
* `latest/index.html` redirects to the newest `job_NNN/`;
* `latest/` moves when a newer report appears;
* `latest/` is not listed as a report row;
* parent indexes link to stable `latest/` aliases;
* old immutable `job_NNN/` URLs remain valid;
* pruning does not delete `latest/` or `history/`.

## Testing Pruning

When changing `prune_reports.py`, verify:

* only old `job_*` report folders are removed;
* `history/` is preserved;
* `latest/` is preserved;
* `index.html` is preserved;
* `.modified_at` is preserved;
* report retention remains predictable.

Pruning must never delete Allure history data needed by the next run.

## Testing Merge Request Comments

Merge request comments are optional.

They must not break report publishing.

Token responsibilities:

```text
GIT_PUSH_TOKEN
  used only for git operations against the Pages storage branch

ALLURE_HISTORY_TOKEN
  used only for GitLab REST API calls, such as MR comments
```

When changing MR comment logic, verify:

* `GIT_PUSH_TOKEN` is not used for GitLab API calls;
* `ALLURE_HISTORY_TOKEN` is used for creating/updating MR comments;
* missing `ALLURE_HISTORY_TOKEN` skips MR comments without failing report publishing;
* API failures are logged clearly;
* existing comments are updated in place when possible;
* comments created by another token/user are not force-updated;
* the report link points to the immutable current `job_NNN/` snapshot.

MR comments must use the immutable current `job_NNN/` snapshot as evidence. The stable `latest/` alias belongs on index and navigation pages, not in MR comments.

Preferred MR comment format:

```markdown
Allure: [report](REPORT_URL) · 42 passed · 2 skipped
```

For issue reports:

```markdown
Allure: [report](REPORT_URL) · **2 issues** · failed 1 · broken 1 · 44 total
```

Keep MR comments compact. Avoid headings, emoji, tables, and duplicate links.

## Testing component changes

When changing `templates/gitlab-allure-history.yml`, check:

* a minimal include still works;
* a custom `environment` still works;
* a custom `pages-branch` still works;
* MR comments still work when enabled;
* MR comments are skipped when disabled;
* missing Allure results fail with a clear diagnostic;
* default values are safe;
* existing documented usage remains valid;
* `allure-history-image-tag` is still handled correctly;
* report publishing still works;
* MR comments remain optional;
* generated Pages layout remains compatible.

Do not add new inputs casually.

Each new input becomes part of the public component contract and must be documented and tested.

Good component inputs affect actual behavior:

* environment;
* pages branch;
* reports to keep;
* Allure results directory;
* MR comment enablement;
* branch publishing rules.

Avoid inputs for cosmetic details unless there is a strong reason.

## Documentation Changes

Update documentation when behavior changes.

Usually affected files:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
```

README should stay user-facing:

* what the project does;
* why it exists;
* how to use it;
* required variables;
* storage layout;
* component inputs;
* concise troubleshooting.

CONTRIBUTING should stay maintainer/contributor-facing:

* how to test;
* how to validate generated indexes;
* how to reason about component changes;
* release checklist;
* project scope.

## Changelog

For user-visible changes, update `CHANGELOG.md`.

Use the current unreleased section.

Group changes under:

```markdown
### Added
### Changed
### Fixed
### Breaking
```

Do not put new unreleased changes under an already released version.

The project uses a year-based versioning scheme:

```text
YYYY.MINOR.PATCH
```

Component tags and runtime image tags are released together and should use the same version.

## Release Workflow

1. Merge the release changes to `master` with an updated changelog.
2. Create a `YYYY.MINOR.PATCH` tag from the validated `master` commit.
3. The tag pipeline includes the component at that tag, builds and pushes the matching runtime image through `build_python`, runs validation and publishing jobs, and creates the GitLab release through `create_release`.
4. After the release succeeds, update the fallback runtime image tag in `.gitlab-ci.yml` for non-tag pipelines.

## Pull Request Checklist

Before opening or merging a pull request, check:

- [ ] Tests pass.
- [ ] Generated index behavior is covered when changed.
- [ ] `latest/` behavior is covered when changed.
- [ ] Pruning behavior is covered when changed.
- [ ] MR comment behavior is covered when changed.
- [ ] README is updated for user-facing changes.
- [ ] CHANGELOG is updated for release-visible changes.
- [ ] No unrelated refactoring is included.
- [ ] No generated report artifacts are committed accidentally.

## Release checklist

Before tagging:

- [ ] Merge request is reviewed and merged to master.
- [ ] Master pipeline is green.
- [ ] GitLab Pages opens.
- [ ] `/dev/` opens.
- [ ] `/dev/master/` opens.
- [ ] `/dev/master/latest/` opens.
- [ ] `latest/` points to the newest immutable `job_NNN/` report.
- [ ] Old `job_NNN/` report links still work.
- [ ] Issue result links still work if affected.
- [ ] MR comment behavior is checked if affected.
- [ ] README version references are updated.
- [ ] The CHANGELOG entry is moved from `unreleased` to released.
- [ ] Component version and runtime image tag match.

After tagging:

- [ ] Release tag is created.
- [ ] Tag pipeline is green.
- [ ] Matching runtime image is published.
- [ ] GitLab release notes are published.
- [ ] Non-tag fallback image in `.gitlab-ci.yml` is updated.

## Design Principles

Prefer:

* static HTML;
* simple CSS;
* small vanilla JavaScript only when useful;
* explicit GitLab CI behavior;
* stable URLs;
* predictable storage layout;
* boring reliability.

Avoid:

* hidden magic;
* large UI rewrites;
* external frontend dependencies;
* backend assumptions;
* over-configurable cosmetic options;
* features that turn the project into a report portal.

The project should solve one problem well:

```text
Publish branch-based Allure report history to GitLab Pages with stable links and no extra infrastructure.
```

## Sponsored and custom work

Out-of-scope requests are not part of the unpaid upstream roadmap. Depending on complexity and fit, they may be considered as sponsored development, private or custom integration work, separately maintained extensions, or downstream forks.

Open an issue before investing significant time in a large out-of-scope change.
