<h1><img src="docs/assets/gitlab-allure-history-logo-readme-tight.png" width="36" height="36" alt="GitLab Allure History logo" align="absmiddle"> GitLab Allure History Publisher</h1>


[![Latest Release](https://img.shields.io/gitlab/v/release/aleksandr-kotlyar/gitlab-allure-history?sort=semver)](https://gitlab.com/aleksandr-kotlyar/gitlab-allure-history/-/releases)

Publish Allure reports with preserved history to GitLab Pages using GitLab CI and static files. No report server, database, web framework, or external storage service is required.

## Scope

This project publishes Allure report history to GitLab Pages using static files only. It is designed for GitLab CI/CD projects, GitLab Pages hosting, immutable per-pipeline report snapshots, stable branch-level `latest/` aliases, and lightweight merge request report links.

It is not a test management system, ReportPortal replacement, backend service, database-backed analytics platform, generic multi-CI report publisher, or object-storage report warehouse.

## Quick Start

Include the component in `.gitlab-ci.yml` and pin a published release tag:

```yaml
include:
  - component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/gitlab-allure-history@2026.2.10
    inputs:
      environment: dev
      pages-branch: gl-pages
      reports-to-keep: "30"

stages:
  - test
  - report

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest --alluredir=allure-results
  artifacts:
    when: always
    paths:
      - allure-results
```

The component adds a `publish-allure-history` job that generates the HTML report, preserves history across runs, pushes the generated content to the storage branch, and publishes GitLab Pages from the main/component pipeline.

> [!WARNING]
> This component publishes the project's GitLab Pages site from `public/`. If the project already uses GitLab Pages for another site, use a dedicated project for Allure history or avoid conflicting Pages deployments.

## Prerequisites

- GitLab Pages enabled for the project.
- A `GIT_PUSH_TOKEN` CI variable with `write_repository` permission.
- Test jobs that publish an `allure-results/` artifact.

The component creates the `gl-pages` persistent storage branch automatically on the first run if it does not exist. The branch stores generated `public/` content and history; it is not a deployment pipeline branch and does not need its own `.gitlab-ci.yml`.

Create a project, group, or personal access token with `write_repository` permission and store it as `GIT_PUSH_TOKEN`. The token must be allowed to create and push to `gl-pages`, including when branch protection is enabled. Mark it protected only if reports are published exclusively from protected branches.

Test jobs must save `allure-results/` with `artifacts.when: always`. They may also publish a `jobid` file containing the test job ID; otherwise, the report job uses its own `CI_JOB_ID` for the snapshot folder.

## Compatibility

| Area | Status | Notes |
| --- | ---: | --- |
| GitLab CI/CD | Supported | Primary target. |
| GitLab CI/CD components | Supported | Recommended integration model. |
| GitLab Pages | Supported | Reports are published as static Pages content. |
| Allure Report 2 | Supported | Current target format. |
| Allure Report 3 | Not verified | Planned research item. |
| pytest | Tested by demo | Used as the reference example. |
| Other Allure-compatible frameworks | Expected | Should work if they produce standard `allure-results`. |
| Self-managed GitLab | Expected | Not fully covered by consumer contract fixtures yet. |
| GitHub Actions | Out of scope | This project is GitLab-native. |

## How It Works

1. Test jobs publish `allure-results/`.
2. The component restores the previous branch history from `gl-pages`.
3. Allure generates a new immutable report snapshot.
4. Static indexes and the stable `latest/` alias are updated.
5. The `public/` tree is committed to `gl-pages` with CI skipped for persistent storage.
6. The same `public/` tree is uploaded by the `publish-allure-history` job and published by GitLab Pages from the main/component pipeline.

## Report Storage Layout

Reports are persisted in the `gl-pages` storage branch. The branch contains generated content, not a separate Pages deployment pipeline:

```text
public/
  index.html
  {environment}/
    index.html
    {branch-slug}/
      index.html
      latest/
        index.html
      history/
      job_NNN/
```

- `latest/` redirects to the newest immutable `job_NNN/` snapshot.
- `history/` is reused by the next run to preserve Allure trends.
- Root, environment, and branch indexes provide navigation.
- Branch folders use `CI_COMMIT_REF_SLUG` to keep paths URL-safe.

## Latest Report Links

Use the stable latest-report URL:

```text
https://<pages-domain>/<project>/<environment>/<branch-slug>/latest/
```

Use an immutable snapshot URL when linking to a specific pipeline result:

```text
https://<pages-domain>/<project>/<environment>/<branch-slug>/job_NNN/
```

`latest/` is a static HTML redirect, not a report copy or symlink.

## Version Pinning

Component and runtime image tags are released as a matched pair. A tagged component reference resolves the matching runtime image tag automatically:

```yaml
include:
  - component: gitlab.com/aleksandr-kotlyar/gitlab-allure-history/gitlab-allure-history@2026.2.10
    inputs:
      environment: dev
```

Use a published release tag for normal use. When using a full commit SHA or branch reference, set the runtime image tag explicitly:

```yaml
include:
  - component: gitlab.com/.../gitlab-allure-history@$CI_COMMIT_SHA
    inputs:
      allure-history-image-tag: "2026.2.10"
```

The version scheme is `YYYY.MINOR.PATCH`. See [CHANGELOG.md](CHANGELOG.md) for release history.

## Component Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `environment` | `dev` | Report environment folder under `public/`. |
| `allure-history-image` | `registry.gitlab.com/...` | Runtime image repository. |
| `allure-history-image-tag` | `$[[ component.version ]]` | Runtime image tag. Set explicitly for SHA or branch component references. |
| `allure-history-tools-dir` | `/opt/gitlab-allure-history` | **Advanced custom image override.** Directory containing `generate_index.py` and `prune_reports.py`. |
| `pages-branch` | `gl-pages` | Persistent storage branch for generated Pages content and Allure history. |
| `reports-to-keep` | `30` | Report snapshots retained per environment and branch. |
| `build-runtime-image` | `false` | **Maintainer/release input.** Build and push this project's runtime image in tag pipelines. |
| `comment-mr` | `false` | Post or update a merge request comment with the current immutable report URL. |

### Optional CI Variables

- `ALLURE_HISTORY_INDEX_DESKTOP_BATCH_SIZE`: rows shown before `Show more...` on desktop. Default `25`; set to `0` for no limit.
- `ALLURE_HISTORY_INDEX_MOBILE_BATCH_SIZE`: rows shown before `Show more...` on mobile. Default `12`; set to `0` for no limit.
- `ALLURE_HISTORY_TOKEN`: token with `api` scope for merge request comments. Without it, comments are skipped.

### GitLab CI Values Used

- `ENV`: report environment folder, populated from the `environment` input.
- `CI_COMMIT_REF_SLUG`: branch report folder.
- `CI_JOB_ID`: fallback report snapshot ID when no `jobid` artifact exists.
- `CI_PAGES_URL`: report URL metadata.
- `CI_PIPELINE_URL`: pipeline URL metadata.

The runner needs network access to pull the runtime image, clone and push the Pages branch, and upload the `public/` artifact.

## Demo

- GitLab project: [gitlab.com/aleksandr-kotlyar/gitlab-allure-history](https://gitlab.com/aleksandr-kotlyar/gitlab-allure-history)
- Published reports: [aleksandr-kotlyar.gitlab.io/gitlab-allure-history](https://aleksandr-kotlyar.gitlab.io/gitlab-allure-history/)

## Troubleshooting

### Storage Branch Cannot Be Created

Check that `GIT_PUSH_TOKEN` is allowed to create and push the configured storage branch. If branch protection requires pre-creation by a maintainer, create the branch once and rerun the pipeline.

### Report Job Cannot Push

Check that `GIT_PUSH_TOKEN` is available to the pipeline, has `write_repository` permission, and is allowed to push to `gl-pages`. Protected variables are unavailable on unprotected branches.

### No Previous History

The first run for a branch has no previous history. The report still publishes, and later runs reuse the generated `history/` folder.

### Branch Name Appears As A Slug

This is expected. Report paths use `CI_COMMIT_REF_SLUG`.

## Roadmap

- Document compatibility with non-pytest Allure producers.
- Investigate Allure Report 3 compatibility.

## Sponsored work

Some requests may be useful for specific teams while remaining outside the core open-source roadmap. Examples include backend services, database-backed analytics, custom dashboards, object storage integrations, non-GitLab CI/CD integrations, custom enterprise workflows, and advanced flaky-test analytics.

These are not planned for the core open-source roadmap, but may be considered as sponsored development, custom integrations, or separately maintained extensions.

## Contributing

Development setup, repository CI details, testing, scope, and release procedures are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
