import pytest
import os
import pandas as pd
from lightcurve_processor.process_lightcurves import process_lightcurve

def test_process_lightcurve(tmp_path):
    # Create a mock lightcurve file
    test_file = tmp_path / "test_lightcurve.txt"
    with open(test_file, "w") as f:
        f.write("TIME,PDCSAP_FLUX\n")
        f.write("0.0,1.0\n")
        f.write("1.0,1.5\n")
        f.write("2.0,NaN\n")
        f.write("3.0,2.0\n")

    output_dir = tmp_path / "processed"
    os.makedirs(output_dir, exist_ok=True)

    # Process the lightcurve
    result_path = process_lightcurve(str(test_file), str(output_dir), gap_threshold=1.5 / 24, sigma_clip=3)

    # Verify output file exists
    assert os.path.exists(result_path)

    # Verify processed file contents
    df = pd.read_csv(result_path)
    assert not df.isna().any().any()  # No NaNs should remain
    assert "flux_normalized" in df.columns  # Ensure the normalized column exists
