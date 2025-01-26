import os
import re
import numpy as np

def group_files_by_metadata(directory):
    """
    Groups lightcurve files by metadata extracted from filenames.
    """
    pattern = re.compile(r'LK_exptime_(\w+)_LK_mission_(TESS|K2)_')
    groups = {}
    for file in os.listdir(directory):
        match = pattern.search(file)
        if match:
            key = (match.group(1), match.group(2))
            groups.setdefault(key, []).append(os.path.join(directory, file))
    return groups

def concatenate_and_fix_gaps(filepaths, gap_threshold=80.0):
    """
    Concatenate lightcurve files and fix gaps larger than the threshold.
    """
    all_data = [np.genfromtxt(f, delimiter=',', skip_header=1) for f in filepaths]
    time, flux = np.concatenate([d[:, 0] for d in all_data]), np.concatenate([d[:, 1] for d in all_data])
    gaps = np.where(np.diff(time) > gap_threshold)[0]
    for idx in gaps:
        time[idx+1:] += time[idx+1] - time[idx] + gap_threshold
    return time, flux
