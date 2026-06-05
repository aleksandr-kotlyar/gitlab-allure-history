from prune_reports import prune_reports


def create_report(path, job_id):
    report_path = path / f"job_{job_id}"
    report_path.mkdir()
    (report_path / "index.html").write_text(str(job_id))
    return report_path


def test_prune_reports_keeps_latest_jobs_by_numeric_id(tmp_path):
    for job_id in [10, 2, 30, 20]:
        create_report(tmp_path, job_id)
    (tmp_path / "history").mkdir()
    (tmp_path / "index.html").write_text("index")

    removed = prune_reports(tmp_path, keep=2)

    assert removed == 2
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "history",
        "index.html",
        "job_20",
        "job_30",
    ]


def test_prune_reports_ignores_missing_path(tmp_path):
    removed = prune_reports(tmp_path / "missing")

    assert removed == 0
