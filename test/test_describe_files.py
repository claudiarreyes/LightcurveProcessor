import pytest
import os
import csv
from lightcurve_processor.describe_files import collect_metadata, write_summary_csv

def test_collect_metadata(tmp_path):
    # Create mock lightcurve files
    filenames = [
        "00001_target_StarA_LK_exptime_120_LK_mission_TESS_LK_author.txt",
        "00001_target_StarA_LK_exptime_120_LK_mission_K2_LK_author.txt",
        "00002_target_StarB_LK_exptime_60_LK_mission_TESS_LK_author.txt",
    ]
    for fname in filenames:
        (tmp_path / fname).touch()

    metadata = collect_metadata(tmp_path)
    assert len(metadata) == 2  # Two unique irows
    assert "00001" in metadata
    assert "00002" in metadata
    assert metadata["00001"]["exptime"]["120"] == ["TESS", "K2"]

def test_write_summary_csv(tmp_path):
    # Mock metadata
    metadata = {
        "00001": {
            "tel_target": "StarA",
            "exptime": {
                "120": ["TESS", "K2"],
            },
        },
        "00002": {
            "tel_target": "StarB",
            "exptime": {
                "60": ["TESS"],
            },
        },
    }

    # Write summary CSV
    output_csv = tmp_path / "summary.csv"
    write_summary_csv(metadata, output_csv)

    # Verify contents
    with open(output_csv, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["irow", "tel_target", "60", "120"]  # Header
    assert rows[1] == ["00001", "StarA", "NO", "TESS,K2"]
    assert rows[2] == ["00002", "StarB", "TESS", "NO"]
