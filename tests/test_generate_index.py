from generate_index import (
    DESKTOP_LIST_BATCH_SIZE,
    DESKTOP_LIST_BATCH_SIZE_ENV,
    MOBILE_LIST_BATCH_SIZE,
    MOBILE_LIST_BATCH_SIZE_ENV,
    index_folder,
    index_tree,
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
    assert "Show more..." not in html


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


def test_index_adds_show_more_controls_for_populated_lists(tmp_path):
    public_dir = tmp_path / "public"
    public_dir.mkdir()

    total_entries = DESKTOP_LIST_BATCH_SIZE + 1
    for index in range(total_entries):
        (public_dir / f"branch-{index:02d}").mkdir()

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert html.count("<tr data-list-row>") == total_entries
    assert '<table data-progressive-list>' in html
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
