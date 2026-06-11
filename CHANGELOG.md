# Changelog

## Release Policy

Component tags and runtime image tags are released together and use the same
version. When you pin a component release tag (e.g. `@2026.2.7`), the
runtime image tag resolves automatically from the component version.

```yaml
include:
  - component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/gitlab-allure-history@2026.2.7
    inputs:
      environment: dev
```

The project uses a year-based versioning scheme:

`YYYY.MINOR.PATCH`

Minor version bumps indicate feature additions. Patch bumps are used for
fixes and maintenance. Breaking changes are called out explicitly in this
changelog.

_Maintainer note:_ after each release, update the fallback image tag in
`.gitlab-ci.yml` so non-tag dogfooding pipelines continue to use a recent
runtime image.

---

## 2026.2.9 (unreleased)

### Added

- Add stable `latest/` aliases for report branch folders.
- Generate `latest/index.html` as a static redirect to the newest
  immutable `job_NNN/` report.
- Add generator footer with `gitlab-allure-history` version metadata
  when available.
- Use GitLab component context (`$[[ component.version ]]`,
  `$[[ component.reference ]]`) — the component now resolves its
  own runtime image tag automatically when included with a tagged
  reference.
- Add `COMPONENT_VERSION` and `COMPONENT_REFERENCE` CI variables
  for script-level access to component metadata.

### Changed

- Update parent index `latest` links to point to stable `latest/`
  aliases instead of concrete `job_NNN/` snapshots.
- Keep immutable `job_NNN/` snapshot links for exact pipeline reports.
- Keep `latest/` internal and exclude it from generated report listings.
- Refine compact report result styling.
- Make demo tests randomly flaky instead of always failing.
- `allure-history-image-tag` input is now optional — defaults to
  `$[[ component.version ]]`. Explicit tag is still required when
  using SHA or branch references.
- `GITLAB_ALLURE_HISTORY_VERSION` fallback chain includes
  `COMPONENT_VERSION` before `unknown`.

### Fixed

- Ensure pruning keeps `latest/` and `history/` while removing only
  old `job_*` report snapshots.

---

## 2026.2.8 (2026-06-08)

### Added

- Add `curl` to the runtime image for merge request comment API calls.

### Changed

- Refine merge request report comment integration.

---

## 2026.2.7 (2026-06-07)

- Require explicit component image tag (`allure-history-image-tag` is now
  mandatory).
- Prepare reusable GitLab CI component structure.
- Stabilize Allure CI template for external consumption.

---

## 2026.2.6 (2026-06-07)

- Fix Allure trend links — report snapshots now link correctly in the
  generated index.

---

## 2026.2.5 (2026-06-07)

- Add Allure summary columns (passed, failed, broken, skipped, unknown)
  to report indexes.

---

## 2026.2.4 (2026-06-07)

- Add latest report links to generated indexes.

---

## 2026.2.3 (2026-06-07)

- Use new runtime image `2026.2.1`.
- Move Allure CI logic into reusable template.
- Move GitLab CI into reusable template.
- Scope open demo reports by environment.
- Keep the latest 30 Allure reports by default (configurable).
- Make index reveal batch size configurable.
- Add progressive index reveal controls.
- Breadcrumb navigation for generated indexes.
- Sticky breadcrumbs and header polish.

---

## 2026.2.2 (2026-06-05)

- Improve Allure history dashboard UX.
- Keep last 20 Allure reports.
- Update Python dependencies.

---

## 2026.2.1 (2026-05-23)

- First semver release after the early prototype stage.
- Rewrite README with clear value and quick-start.
- Add "modified at" column to report storage tree.
- Harden GitLab Pages publish flow.
- Split gate and demo test jobs.
- Add pytest `--env` option and fixtures.

---

## Before 2026.2.1

Initial prototype with basic Allure report generation and GitLab Pages
publishing.
