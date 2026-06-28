# Changelog

## Release policy

- Component releases pin a tested Core Allure History runtime image.
- Versions follow the `YYYY.MINOR.PATCH` scheme.
- Breaking changes are called out explicitly.

## 2026.2.11 (2026-06-28)

### Changed

- The publish-template helper scripts were moved into
  Core Allure History, leaving the GitLab component as a thinner wrapper around
  the shared runtime.
- The default runtime image now points to
  `registry.gitlab.com/aleksandr-kotlyar/allure-history-core:2026.2.11`.

### Breaking

- Removed runtime image override and maintainer-only inputs:
  `allure-history-image`, `allure-history-image-tag`,
  `allure-history-tools-dir`, and `build-runtime-image`.
- The component now owns the tested Core Allure History runtime pin directly;
  consumers should pin only the GitLab component version.

## 2026.2.10 (2026-06-22)

### Changed

- Environment branch indexes now separate latest report links from branch
  history links.
- Root environment indexes keep environment rows visible instead of linking each
  environment directly to a nested latest report.
- Generated footers now underline the project link and link component versions
  to the GitLab CI/CD Catalog page.

### Documentation

- README examples now point to `2026.2.10` and show the project logo in the
  header.

### Repository CI

- Consumer contract child pipelines now run their verification jobs in merge
  request/downstream pipeline contexts.
- Non-tag dogfood and consumer contract pipelines use the latest published
  `2026.2.10` fallback runtime image.
- Project CI uses concurrent-slot-specific clone paths to avoid local runner
  checkout collisions.

## 2026.2.9 (2026-06-14)

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
