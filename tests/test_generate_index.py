import json

from generate_index import (
    DESKTOP_LIST_BATCH_SIZE,
    DESKTOP_LIST_BATCH_SIZE_ENV,
    LATEST_DIRNAME,
    MOBILE_LIST_BATCH_SIZE,
    MOBILE_LIST_BATCH_SIZE_ENV,
    SHOW_FOOTER_ENV,
    VERSION_ENV,
    generator_footer_html,
    index_folder,
    index_tree,
)


def write_summary(report_dir, statistic, duration):
    widgets_dir = report_dir / "widgets"
    widgets_dir.mkdir()
    (widgets_dir / "summary.json").write_text(
        json.dumps({"statistic": statistic, "time": {"duration": duration}}),
        encoding="utf-8",
    )


def test_index_folder_creates_empty_index(tmp_path):
    public_dir = tmp_path / "public"

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert index_path == public_dir / "index.html"
    assert "No reports yet." in html
    assert "Index of" not in html
    assert "gitlab-allure-history" in html
    assert 'aria-current="page">gitlab-allure-history</span>' in html
    assert '<td class="name-cell" colspan="2">No reports yet.</td>' in html
    assert "Show more..." not in html


def test_root_index_shows_project_intro_and_keeps_listing_links(tmp_path):
    public_dir = tmp_path / "public"
    (public_dir / "dev").mkdir(parents=True)

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert '<section class="hero" aria-label="Project summary">' in html
    assert "<h2>GitLab Allure History Publisher</h2>" in html
    assert "<h1>GitLab Allure History Publisher</h1>" not in html
    assert "Branch-based Allure report history on GitLab Pages." in html
    assert "No server. No database. No external storage." in html
    assert '<th class="name-cell">Name</th>' in html
    assert '<th class="latest-report-cell">Latest report</th>' not in html
    assert 'href="dev/">dev/</a>' in html
    assert html.index('class="hero"') < html.index('class="index-table')


def test_mobile_hero_typography_keeps_listing_primary(tmp_path):
    public_dir = tmp_path / "public"

    html = index_folder(public_dir).read_text(encoding="utf-8")

    assert "@media (max-width: 640px)" in html
    assert ".hero h2 {" in html
    assert "padding: 14px 16px;" in html
    assert "font-size: 1.12rem;" in html
    assert "font-size: 0.88rem;" in html
    assert "line-height: 1.45;" in html


def test_theme_toggle_has_hover_and_keyboard_focus_affordance(tmp_path):
    public_dir = tmp_path / "public"

    html = index_folder(public_dir).read_text(encoding="utf-8")

    assert ".theme-toggle:hover,\n        .theme-toggle:focus-visible {" in html
    assert "border-color: var(--link);" in html
    assert (
        "box-shadow: 0 0 0 3px "
        "color-mix(in srgb, var(--link) 22%, transparent);"
        in html
    )
    assert (
        "background: color-mix(in srgb, var(--link) 10%, var(--panel));"
        in html
    )


def test_mobile_metadata_typography_keeps_values_secondary(tmp_path):
    public_dir = tmp_path / "public"

    html = index_folder(public_dir).read_text(encoding="utf-8")

    assert "@media (max-width: 640px)" in html
    assert ".entry-meta,\n            .entry-meta-label,\n            .entry-meta-link {" in html
    assert "td[data-label] {" in html
    assert "column-gap: 8px;" in html
    assert "font-size: 0.82rem;" in html
    assert "color: var(--muted);" in html
    assert "font-weight: 500;" in html
    assert "line-height: 1.35;" in html
    assert "font: inherit;" in html
    assert "letter-spacing: 0;" in html
    assert "text-transform: none;" in html
    assert "font-variant-numeric: tabular-nums;" in html


def test_non_root_indexes_do_not_show_project_intro(tmp_path):
    public_dir = tmp_path / "public"
    env_dir = public_dir / "dev"
    branch_dir = env_dir / "feature-login"
    report_dir = branch_dir / "job_101"
    history_dir = branch_dir / "history"
    report_dir.mkdir(parents=True)
    history_dir.mkdir()

    env_html = index_folder(env_dir).read_text(encoding="utf-8")
    branch_html = index_folder(branch_dir).read_text(encoding="utf-8")
    report_html = index_folder(report_dir).read_text(encoding="utf-8")
    history_html = index_folder(history_dir).read_text(encoding="utf-8")
    latest_html = (branch_dir / LATEST_DIRNAME / "index.html").read_text(
        encoding="utf-8"
    )

    for html in (env_html, branch_html, report_html, history_html, latest_html):
        assert 'class="hero"' not in html
        assert "GitLab Allure History Publisher" not in html

    assert (
        '<a class="entry-link latest-report-link" '
        'href="feature-login/latest/">feature-login</a>'
    ) in env_html
    assert '<a class="history-link" href="feature-login/"' in env_html
    assert 'href="feature-login/">feature-login/</a>' not in env_html
    assert 'href="job_101/">job_101/</a>' in branch_html


def test_index_escapes_labels_and_encodes_links(tmp_path):
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    branch_dir = public_dir / "feature <one>&two"
    report_file = public_dir / "job 42 & notes.txt"
    branch_dir.mkdir()
    report_file.write_text("report notes", encoding="utf-8")

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert 'href="feature%20%3Cone%3E%26two/"' in html
    assert "feature &lt;one&gt;&amp;two/" in html
    assert 'href="job%2042%20%26%20notes.txt"' in html
    assert "job 42 &amp; notes.txt" in html


def test_index_sorts_directories_before_files(tmp_path):
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    (public_dir / "z_file.txt").write_text("z", encoding="utf-8")
    (public_dir / "B_dir").mkdir()
    (public_dir / "a_dir").mkdir()
    (public_dir / "A_file.txt").write_text("a", encoding="utf-8")

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.index("a_dir/") < html.index("B_dir/")
    assert html.index("B_dir/") < html.index("A_file.txt")
    assert html.index("A_file.txt") < html.index("z_file.txt")


def test_index_pins_master_first(tmp_path):
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    master_dir = public_dir / "master"
    feature_dir = public_dir / "feature"
    master_dir.mkdir()
    feature_dir.mkdir()
    (master_dir / ".modified_at").write_text("2026-06-05T22:15:00Z\n", encoding="utf-8")
    (feature_dir / ".modified_at").write_text("2026-06-06T08:00:00Z\n", encoding="utf-8")

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.index("master/") < html.index("feature/")


def test_index_links_parent_breadcrumbs(tmp_path):
    report_dir = tmp_path / "public" / "master" / "job_101"
    report_dir.mkdir(parents=True)

    index_path = index_folder(report_dir)

    html = index_path.read_text(encoding="utf-8")
    assert '<a href="../../">gitlab-allure-history</a>' in html
    assert '<a href="../">master</a>' in html
    assert 'aria-current="page">job_101</span>' in html


def test_index_omits_parent_table_row_when_breadcrumbs_are_available(tmp_path):
    branch_dir = tmp_path / "public" / "master"
    (branch_dir / "job_101").mkdir(parents=True)

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert '<td class="name-cell"><a href="../">../</a></td>' not in html
    assert '<a href="../">gitlab-allure-history</a>' in html


def test_index_tree_updates_navigation_indexes_without_touching_reports(tmp_path):
    public_dir = tmp_path / "public"
    branch_dir = public_dir / "master"
    report_dir = branch_dir / "job_101"
    history_dir = branch_dir / "history"
    feature_dir = public_dir / "feature"
    report_dir.mkdir(parents=True)
    history_dir.mkdir()
    feature_dir.mkdir()
    report_index = report_dir / "index.html"
    report_index.write_text("allure report", encoding="utf-8")

    index_paths = index_tree(public_dir)

    assert public_dir / "index.html" in index_paths
    assert branch_dir / "index.html" in index_paths
    assert feature_dir / "index.html" in index_paths
    assert report_dir / "index.html" not in index_paths
    assert not (history_dir / "index.html").exists()
    assert report_index.read_text(encoding="utf-8") == "allure report"


def test_index_handles_branch_report_folder(tmp_path):
    branch_dir = tmp_path / "public" / "feature-login"
    (branch_dir / "history").mkdir(parents=True)
    (branch_dir / "job_101").mkdir()

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert 'href="history/"' not in html
    assert 'href="job_101/"' in html


def test_index_marks_latest_report_and_moves_badge_on_regeneration(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    job_101 = branch_dir / "job_101"
    job_102 = branch_dir / "job_102"
    job_101.mkdir(parents=True)
    job_102.mkdir()
    (job_101 / ".modified_at").write_text("2026-06-05T22:15:00Z\n", encoding="utf-8")
    (job_102 / ".modified_at").write_text("2026-06-06T08:00:00Z\n", encoding="utf-8")

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count('class="latest-badge">latest</span>') == 1
    assert (
        'href="job_102/">job_102/</a> <span class="latest-badge">latest</span>'
        in html
    )

    job_103 = branch_dir / "job_103"
    job_103.mkdir()
    (job_103 / ".modified_at").write_text("2026-06-07T09:30:00Z\n", encoding="utf-8")
    index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count('class="latest-badge">latest</span>') == 1
    assert (
        'href="job_103/">job_103/</a> <span class="latest-badge">latest</span>'
        in html
    )
    assert (
        'href="job_102/">job_102/</a> <span class="latest-badge">latest</span>'
        not in html
    )


def test_report_index_shows_allure_summary_columns(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    report_dir = branch_dir / "job_101"
    report_dir.mkdir(parents=True)
    write_summary(
        report_dir,
        {
            "failed": 1,
            "broken": 0,
            "skipped": 1,
            "passed": 2,
            "unknown": 0,
            "total": 4,
        },
        65_000,
    )

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert '<th class="result-cell">Result</th>' in html
    assert '<th class="duration-cell">Duration</th>' in html
    assert "--allure-passed: #97cc64;" in html
    assert "--allure-failed: #fd5a3e;" in html
    assert "--allure-broken: #ffd050;" in html
    assert "--allure-skipped: #aaaaaa;" in html
    assert "--allure-unknown: #d35ebe;" in html
    assert 'class="summary-compact issue"' in html
    assert "Failed: 1" in html
    assert "Skipped: 1" in html
    assert "Passed: 2" in html
    assert "1 issue" in html
    assert "4 total" in html
    assert 'href="job_101/#categories"' in html
    assert 'data-label="Duration">1m 05s</td>' in html


def test_report_index_falls_back_when_allure_summary_is_missing_or_invalid(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    missing_summary = branch_dir / "job_101"
    invalid_summary = branch_dir / "job_102"
    missing_summary.mkdir(parents=True)
    (invalid_summary / "widgets").mkdir(parents=True)
    (invalid_summary / "widgets" / "summary.json").write_text(
        "not json",
        encoding="utf-8",
    )

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count('data-label="Result">n/a</td>') == 2
    assert html.count('data-label="Duration">n/a</td>') == 2


def test_report_index_omits_zero_count_badges(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    report_dir = branch_dir / "job_101"
    report_dir.mkdir(parents=True)
    write_summary(
        report_dir,
        {
            "failed": 0,
            "broken": 0,
            "skipped": 0,
            "passed": 1,
            "unknown": 0,
            "total": 1,
        },
        1_000,
    )

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count('class="summary-compact') == 1
    assert 'summary-compact passed' in html
    assert "1 passed" in html
    assert "Passed: 1" in html


def test_navigation_indexes_exclude_report_summary_columns(tmp_path):
    public_dir = tmp_path / "public"
    env_dir = public_dir / "dev"
    branch_dir = env_dir / "feature-login"
    report_dir = branch_dir / "job_101"
    report_dir.mkdir(parents=True)
    write_summary(
        report_dir,
        {"failed": 0, "broken": 0, "skipped": 0, "passed": 1, "unknown": 0, "total": 1},
        1_000,
    )

    root_index_path = index_folder(public_dir)
    env_index_path = index_folder(env_dir)

    root_html = root_index_path.read_text(encoding="utf-8")
    env_html = env_index_path.read_text(encoding="utf-8")
    assert '<th class="result-cell">Result</th>' not in root_html
    assert '<th class="duration-cell">Duration</th>' not in root_html
    assert '<th class="result-cell">Result</th>' not in env_html
    assert '<th class="duration-cell">Duration</th>' not in env_html


def test_env_index_links_each_branch_to_latest_report(tmp_path):
    env_dir = tmp_path / "public" / "dev"
    branch_dir = env_dir / "feature-login"
    report_dir = branch_dir / "job_101"
    report_dir.mkdir(parents=True)

    index_folder(branch_dir)
    index_path = index_folder(env_dir)

    html = index_path.read_text(encoding="utf-8")
    assert '<th class="latest-report-cell">Latest report</th>' in html
    assert '<th class="history-cell">History</th>' in html
    assert (
        '<a class="entry-link latest-report-link" '
        'href="feature-login/latest/">feature-login</a>'
    ) in html
    assert '<a class="history-link" href="feature-login/"' in html
    assert 'href="feature-login/">feature-login/</a>' not in html
    assert 'class="entry-separator"' not in html
    assert 'class="entry-latest-link"' not in html
    assert html.count('href="feature-login/"') == 1


def test_root_index_keeps_environment_rows_visible(tmp_path):
    public_dir = tmp_path / "public"
    old_report = public_dir / "dev" / "master" / "job_101"
    latest_report = public_dir / "dev" / "feature-login" / "job_102"
    beta_report = public_dir / "beta" / "release" / "job_103"
    old_report.mkdir(parents=True)
    latest_report.mkdir(parents=True)
    beta_report.mkdir(parents=True)
    (old_report / ".modified_at").write_text("2026-06-05T22:15:00Z\n", encoding="utf-8")
    (latest_report / ".modified_at").write_text(
        "2026-06-06T08:00:00Z\n", encoding="utf-8"
    )
    (beta_report / ".modified_at").write_text(
        "2026-06-07T09:30:00Z\n", encoding="utf-8"
    )

    index_tree(public_dir)

    index_path = public_dir / "index.html"

    html = index_path.read_text(encoding="utf-8")
    assert 'href="dev/">dev/</a>' in html
    assert 'href="beta/">beta/</a>' in html
    assert "feature-login" not in html
    assert "release" not in html
    assert '<th class="latest-report-cell">Latest report</th>' not in html
    assert '<th class="history-cell">History</th>' not in html


def test_index_adds_show_more_controls_for_populated_lists(tmp_path):
    public_dir = tmp_path / "public"
    public_dir.mkdir()

    total_entries = DESKTOP_LIST_BATCH_SIZE + 1
    for index in range(total_entries):
        (public_dir / f"branch-{index:02d}").mkdir()

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count("<tr data-list-row>") == total_entries
    assert 'data-progressive-list' in html
    assert '<div class="list-controls" hidden>' in html
    assert '<span class="list-count" aria-live="polite"></span>' in html
    assert '<button class="show-more" type="button">Show more...</button>' in html
    assert f"media.matches ? {MOBILE_LIST_BATCH_SIZE} : {DESKTOP_LIST_BATCH_SIZE}" in html


def test_index_uses_configured_show_more_batch_sizes(tmp_path, monkeypatch):
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    monkeypatch.setenv(DESKTOP_LIST_BATCH_SIZE_ENV, "7")
    monkeypatch.setenv(MOBILE_LIST_BATCH_SIZE_ENV, "4")

    for index in range(8):
        (public_dir / f"branch-{index:02d}").mkdir()

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert "Show more..." in html
    assert "media.matches ? 4 : 7" in html


def test_index_disables_show_more_with_zero_batch_sizes(tmp_path, monkeypatch):
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    monkeypatch.setenv(DESKTOP_LIST_BATCH_SIZE_ENV, "0")
    monkeypatch.setenv(MOBILE_LIST_BATCH_SIZE_ENV, "0")

    for index in range(DESKTOP_LIST_BATCH_SIZE + 1):
        (public_dir / f"branch-{index:02d}").mkdir()

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert "Show more..." not in html
    assert '<div class="list-controls" hidden>' not in html
    assert html.count("<tr data-list-row>") == DESKTOP_LIST_BATCH_SIZE + 1


def test_latest_alias_generated_for_branch_folder(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    (branch_dir / "job_101").mkdir(parents=True)
    (branch_dir / "job_102").mkdir()
    (branch_dir / "job_101" / ".modified_at").write_text(
        "2026-06-05T22:15:00Z\n", encoding="utf-8"
    )
    (branch_dir / "job_102" / ".modified_at").write_text(
        "2026-06-06T08:00:00Z\n", encoding="utf-8"
    )

    index_folder(branch_dir)

    latest_index = branch_dir / LATEST_DIRNAME / "index.html"
    assert latest_index.is_file()


def test_latest_alias_redirect_target(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    (branch_dir / "job_101").mkdir(parents=True)
    (branch_dir / "job_101" / ".modified_at").write_text(
        "2026-06-05T22:15:00Z\n", encoding="utf-8"
    )

    index_folder(branch_dir)

    html = (branch_dir / LATEST_DIRNAME / "index.html").read_text(encoding="utf-8")
    assert 'url=../job_101/' in html
    assert '<a href="../job_101/">' in html


def test_latest_alias_moves_after_newer_report(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    (branch_dir / "job_101").mkdir(parents=True)
    (branch_dir / "job_101" / ".modified_at").write_text(
        "2026-06-05T22:15:00Z\n", encoding="utf-8"
    )
    (branch_dir / "job_102").mkdir()
    (branch_dir / "job_102" / ".modified_at").write_text(
        "2026-06-06T08:00:00Z\n", encoding="utf-8"
    )

    index_folder(branch_dir)

    html = (branch_dir / LATEST_DIRNAME / "index.html").read_text(encoding="utf-8")
    assert 'url=../job_102/' in html

    (branch_dir / "job_103").mkdir()
    (branch_dir / "job_103" / ".modified_at").write_text(
        "2026-06-07T09:30:00Z\n", encoding="utf-8"
    )
    index_folder(branch_dir)

    html = (branch_dir / LATEST_DIRNAME / "index.html").read_text(encoding="utf-8")
    assert 'url=../job_103/' in html
    assert 'url=../job_102/' not in html


def test_latest_alias_excluded_from_index_listings(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    (branch_dir / "job_101").mkdir(parents=True)
    (branch_dir / "job_101" / ".modified_at").write_text(
        "2026-06-05T22:15:00Z\n", encoding="utf-8"
    )

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert 'href="latest/"' not in html
    assert 'href="job_101/"' in html


def test_latest_alias_not_generated_for_env_folder(tmp_path):
    env_dir = tmp_path / "public" / "dev"
    branch_dir = env_dir / "feature-login"
    (branch_dir / "job_101").mkdir(parents=True)

    index_folder(env_dir)

    assert not (env_dir / LATEST_DIRNAME).exists()


def test_latest_alias_not_generated_for_empty_branch(tmp_path):
    branch_dir = tmp_path / "public" / "dev" / "feature-login"
    branch_dir.mkdir(parents=True)

    index_folder(branch_dir)

    assert not (branch_dir / LATEST_DIRNAME).exists()


def test_latest_alias_not_generated_for_report_folder(tmp_path):
    report_dir = tmp_path / "public" / "dev" / "feature-login" / "job_101"
    report_dir.mkdir(parents=True)

    index_folder(report_dir)

    assert not (report_dir / LATEST_DIRNAME).exists()


def test_generator_footer_renders_without_version(monkeypatch):
    monkeypatch.delenv(VERSION_ENV, raising=False)
    monkeypatch.setenv(SHOW_FOOTER_ENV, "true")

    html = generator_footer_html()

    assert 'Generated by <a href="https://gitlab.com/aleksandr-kotlyar/gitlab-allure-history">gitlab-allure-history</a>' in html
    assert "v" not in html


def test_generator_footer_renders_with_version(monkeypatch):
    monkeypatch.setenv(VERSION_ENV, "2026.2.8")
    monkeypatch.setenv(SHOW_FOOTER_ENV, "true")

    html = generator_footer_html()

    assert '<span class="generator-footer-content">' in html
    assert "gitlab-allure-history" in html
    assert '<span class="dot-separator">\u00b7</span>' in html
    assert '<span class="generator-version">2026.2.8</span>' in html
    assert "2026.2.8" in html


def test_generator_footer_skips_moving_refs(monkeypatch):
    for ref in ("latest", "master", "main"):
        monkeypatch.setenv(VERSION_ENV, ref)
        monkeypatch.setenv(SHOW_FOOTER_ENV, "true")
        html = generator_footer_html()
        assert "gitlab-allure-history" in html
        assert ref not in html


def test_generator_footer_escapes_version(monkeypatch):
    monkeypatch.setenv(VERSION_ENV, '<script>alert(1)</script>')
    monkeypatch.setenv(SHOW_FOOTER_ENV, "true")

    html = generator_footer_html()

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html


def test_generator_footer_can_be_disabled(monkeypatch):
    monkeypatch.setenv(VERSION_ENV, "2026.2.8")
    monkeypatch.setenv(SHOW_FOOTER_ENV, "false")

    assert generator_footer_html() == ""
