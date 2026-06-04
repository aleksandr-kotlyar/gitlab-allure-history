import shutil
import sys
from pathlib import Path


DEFAULT_REPORTS_TO_KEEP = 20


def job_id(report_dir):
    try:
        return int(report_dir.name.removeprefix("job_"))
    except ValueError:
        return -1


def prune_reports(path, keep=DEFAULT_REPORTS_TO_KEEP):
    reports_dir = Path(path)
    if not reports_dir.exists():
        print(f"Reports path does not exist: {reports_dir}")
        return 0

    job_reports = sorted(
        (
            child
            for child in reports_dir.iterdir()
            if child.is_dir() and child.name.startswith("job_")
        ),
        key=job_id,
    )
    reports_to_delete = job_reports[:-keep] if keep > 0 else job_reports

    for report in reports_to_delete:
        shutil.rmtree(report)

    print(
        f"Pruned {len(reports_to_delete)} report(s) from {reports_dir}; "
        f"kept {len(job_reports) - len(reports_to_delete)}"
    )
    return len(reports_to_delete)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 prune_reports.py <reports_path> [reports_to_keep]")

    reports_to_keep = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_REPORTS_TO_KEEP
    prune_reports(sys.argv[1], reports_to_keep)
