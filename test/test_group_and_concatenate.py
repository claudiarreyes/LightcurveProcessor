import pytest
import os
from lightcurve_processor.group_and_concatenate import group_files_by_metadata, concatenate_and_fix_gaps

def test_group_files_by_metadata(tmp_path):
    # Create mock lightcurve files
    files = [
        "00001_target_StarA_LK_exptime_120_LK_mission_TESS_LK_author.txt",
        "00001_target_StarA_LK_exptime_120_LK_mission_K2_LK_author.txt",
        "00002_target_StarB_LK_exptime_60_LK_mission_TESS_LK_author.txt",
    ]
    for f in files:
        (tmp_path / f).touch()

    groups = group_files_by_metadata(tmp_path)
    assert len(groups) == 2  # Two groups (one for each unique prefix)
    assert ("00001", "120", "TESS") in groups
    assert ("00001", "120", "K2") in groups

def test_concatenate_and_fix_gaps():
    # Mock lightcurve data
    time = [0, 1, 2, 100, 101, 102]
    flux = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]

    # Fix gaps larger than 10 units
    new_time, new_flux, is_shifted = concatenate_and_fix_gaps([time, flux], gap_threshold=10)
    assert is_shifted  # Ensure gaps were detected and fixed
    assert len(new_time) == len(time)  # Verify time array length
