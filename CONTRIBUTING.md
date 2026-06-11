# Contributing

Thanks for your interest in improving `gitlab-allure-history`.

This project is a lightweight GitLab CI component for publishing branch-based Allure report history to GitLab Pages.

The main goal is to stay small, static, and GitLab-native.

## Scope

Good contributions:

* improve GitLab CI component usability;
* improve generated static index pages;
* improve Allure report history preservation;
* improve `latest/` report aliases;
* improve merge request report comments;
* improve documentation and examples;
* improve tests for generated HTML, pruning, and component behavior;
* fix bugs in report publishing, history reuse, or index generation.

Out of scope:

* backend services;
* databases;
* custom report portal features;
* replacing Allure UI;
* test management functionality;
* analytics dashboards;
* frontend frameworks;
* authentication/authorization layers;
* long-running infrastructure outside GitLab CI and GitLab Pages.

This project should remain a static report publisher, not a mini ReportPortal.

## Development Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run only non-demo tests:

```bash
pytest -m "not demo"
```

Run demo tests:

```bash
pytest -m "demo"
```

Demo tests may intentionally produce non-green Allure states. They exist to generate meaningful example reports.

## Testing Generated Indexes

The generated index pages are part of the product.

When changing `generate_index.py`, check that generated indexes still work for:

* root index;
* environment index;
* branch/report index;
* report rows with passed results;
* report rows with issues;
* `latest/` aliases;
* hidden/internal folders;
* light and dark themes if affected.

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
* `latest/` links are not shown by default in MR comments;
* the report link points to the immutable current `job_NNN/` snapshot.

Preferred MR comment format:

```markdown
Allure: [report](REPORT_URL) · 42 passed · 2 skipped
```

For issue reports:

```markdown
Allure: [report](REPORT_URL) · **2 issues** · failed 1 · broken 1 · 44 total
```

Keep MR comments compact. Avoid headings, emoji, tables, and duplicate links.

## Testing GitLab Component Changes

When changing `templates/gitlab-allure-history.yml`, check:

* component inputs still work;
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
* limitations.

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

## Pull Request Checklist

Before opening or merging a pull request, check:

```text
[ ] Tests pass.
[ ] Generated index behavior is covered when changed.
[ ] latest/ behavior is covered when changed.
[ ] pruning behavior is covered when changed.
[ ] MR comment behavior is covered when changed.
[ ] README is updated for user-facing changes.
[ ] CHANGELOG is updated for release-visible changes.
[ ] No unrelated refactoring is included.
[ ] No generated report artifacts are committed accidentally.
```

## Release Checklist

Before tagging a release:

```text
[ ] Merge request is reviewed and merged to master.
[ ] Master pipeline is green.
[ ] GitLab Pages root index opens.
[ ] Environment index opens.
[ ] Branch report index opens.
[ ] latest/ opens and points to the newest job_NNN/ report.
[ ] Old job_NNN/ report links still work.
[ ] Issue result links still work if affected.
[ ] MR comment behavior is checked if affected.
[ ] README matches current behavior.
[ ] CHANGELOG contains the release entry.
[ ] Component version and runtime image tag match.
[ ] Release tag is created.
[ ] GitLab release notes are published.
```

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
