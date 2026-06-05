from generate_index import index_folder


def test_index_folder_creates_empty_index(tmp_path):
    public_dir = tmp_path / "public"

    index_path = index_folder(public_dir)

    html = index_path.read_text(encoding="utf-8")
    assert index_path == public_dir / "index.html"
    assert "No reports yet." in html
    assert "Index of" not in html
    assert "gitlab-allure-history" in html


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


def test_index_handles_branch_report_folder(tmp_path):
    branch_dir = tmp_path / "public" / "feature-login"
    (branch_dir / "history").mkdir(parents=True)
    (branch_dir / "job_101").mkdir()

    index_path = index_folder(branch_dir)

    html = index_path.read_text(encoding="utf-8")
    assert 'href="history/"' not in html
    assert 'href="job_101/"' in html
