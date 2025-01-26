from lightcurve_processor.utils import parse_filename_metadata

def test_parse_filename_metadata():
    filename = "00001_target_StarA_LK_exptime_120_LK_mission_TESS_LK_author.txt"
    metadata = parse_filename_metadata(filename)

    assert metadata["irow"] == "00001"
    assert metadata["tel_target"] == "StarA"
    assert metadata["exptime"] == "120"
    assert metadata["mission"] == "TESS"
