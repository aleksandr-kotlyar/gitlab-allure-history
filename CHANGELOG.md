# Changelog

## Release policy

- Component tags and runtime image tags use the same version.
- Tagged component includes resolve the runtime image tag from the component
  version by default.
- Versions follow the `YYYY.MINOR.PATCH` scheme.
- Breaking changes are called out explicitly.
- An explicit `allure-history-image-tag` is only needed for SHA or branch
  component references.

## 2026.2.9 (unreleased)

### Added

- Stable `latest/` aliases for branch report folders.
- Static redirects from `latest/` to the newest immutable `job_NNN/` report.
- Generator footer with version metadata.
- Component version propagation for generated reports.

### Changed

- Parent indexes link to stable `latest/` aliases.
- Immutable `job_NNN/` report snapshots remain available.
- Runtime image tag defaults to the included component version.
- Compact report result styling refined.
- Demo tests are randomly flaky instead of always failing.

### Fixed

- Pruning keeps `latest/` and `history/`.
- Internal `latest/` aliases are excluded from generated report listings.

## 2026.2.8

- Add runtime `curl` support for merge request comment API calls.
- Refine merge request report comment integration.

## 2026.2.x early releases

- Branch-based Allure report publishing to GitLab Pages.
- Preserved Allure history between pipeline runs.
- Generated report indexes for environments, branches, jobs, and reports.
- Summary columns, breadcrumbs, modified dates, and progressive reveal controls.
- Configurable report retention.
- Reusable GitLab CI component structure.
- Stabilized trend links and generated report navigation.
- README and quick-start improvements.

## Before 2026.2.1

Initial prototype with basic Allure report generation and GitLab Pages
publishing.
