from generate_index import index_folder


def create_report(path, name, modified_at=None):
    report_path = path / name
    report_path.mkdir()
    if modified_at is not None:
        (report_path / ".modified_at").write_text(modified_at + "\n", encoding="utf-8")
    return report_path


def test_index_sorts_reports_by_modified_at_descending(tmp_path):
    create_report(tmp_path, "job_20", "2024-02-01T10:00:00Z")
    create_report(tmp_path, "job_30", "2024-03-01T12:00:00Z")

    index_folder(tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert index_html.index("job_30") < index_html.index("job_20")
    assert "01-Mar-2024 12:00" in index_html
    assert "01-Feb-2024 10:00" in index_html


def test_index_sorts_legacy_reports_by_numeric_job_id_descending(tmp_path):
    create_report(tmp_path, "job_10")
    create_report(tmp_path, "job_2")

    index_folder(tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert index_html.index("job_10") < index_html.index("job_2")


def test_index_hides_history_directory(tmp_path):
    create_report(tmp_path, "job_1", "2024-01-01T01:00:00Z")
    (tmp_path / "history").mkdir()

    index_folder(tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "href='history'" not in index_html


def test_index_hides_parent_link_for_public_root(tmp_path, monkeypatch):
    public_path = tmp_path / "public"
    public_path.mkdir()
    create_report(public_path, "job_1", "2024-01-01T01:00:00Z")
    monkeypatch.chdir(tmp_path)

    index_folder("public")

    index_html = (public_path / "index.html").read_text(encoding="utf-8")
    assert "href='../'" not in index_html


def test_index_keeps_parent_link_for_nested_directory(tmp_path):
    nested_path = tmp_path / "public" / "main"
    nested_path.mkdir(parents=True)
    create_report(nested_path, "job_1", "2024-01-01T01:00:00Z")

    index_folder(nested_path)

    index_html = (nested_path / "index.html").read_text(encoding="utf-8")
    assert "href='../'" in index_html
