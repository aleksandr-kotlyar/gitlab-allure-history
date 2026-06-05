# GitLab Allure History Publisher

Publish **Allure reports with history** to **GitLab Pages** automatically on every pipeline run.

This template solves the common problem: reports are not lost between runs, and trend/history stays available per branch.

## Value

- Branch-based Allure report history
- Automatic GitLab Pages publishing
- Simple HTML storage index for navigation
- Clear split between blocking (`gate`) and non-blocking (`demo`) tests

## How it works

1. `test_gate` runs core tests (blocks pipeline on failure).
2. `test_demo` runs demo tests (does not block pipeline).
3. `allure` job:
   - pulls previous branch `history`,
   - generates a new Allure report,
   - stores it under `gl-pages/public/<branch>/job_<id>`,
   - updates index pages with a `modified at` column,
   - pushes updates to `gl-pages`.
4. GitLab Pages serves the `public` content.

## Report storage layout

- `public/<branch>/job_<id>/` — report snapshot for a run
- `public/<branch>/history/` — Allure trend data
- `public/index.html` and `public/<branch>/index.html` — storage tree index

## Quick start

1. Enable GitLab Pages in project settings.
2. Create branch `gl-pages`.
3. Add CI variable:
   - `GIT_PUSH_TOKEN` (masked + protected, with `write_repository` permission)
4. Run pipeline.
5. Open Pages URL and verify report tree.

## Local run

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pytest -m "not demo"
./.venv/bin/pytest -m "demo"
```

## Key files

- `.gitlab-ci.yml` — CI/CD flow
- `generate_index.py` — HTML index generation for report storage
- `pytest.ini` — pytest config and markers
- `tests/` — sample tests

## Demo

- GitLab mirror: [gitlab.com/aleksandr-kotlyar/gitlab-allure-history](https://gitlab.com/aleksandr-kotlyar/gitlab-allure-history)
- Pages report: [aleksandr-kotlyar.gitlab.io/gitlab-allure-history](https://aleksandr-kotlyar.gitlab.io/gitlab-allure-history/)

## License

MIT
