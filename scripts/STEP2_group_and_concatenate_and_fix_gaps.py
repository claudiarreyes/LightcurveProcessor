import os
import re
import glob
import numpy as np

def find_groups(directory):
    """
    Returns a dictionary where the key is (prefix5, exptimeXXXX, mission)
    and the value is a list of filepaths belonging to that group.

    We assume filenames contain something like:
      <prefix5>...LK_exptime_XXXX_LK_mission_TESS_Sector_XX_LK_author.txt
      or
      <prefix5>...LK_exptime_XXXX_LK_mission_K2_Campaign_XX_LK_author.txt

    Example captures:
      - prefix5: first 5 characters of filename
      - exptimeXXXX from 'LK_exptime_(XXXX)_'
      - mission from 'LK_mission_(TESS|K2)_'
    """

    # Regex:
    #   1) first group: captures exptimeXXXX from  LK_exptime_(\w+)_ 
    #   2) second group: captures TESS or K2 from  LK_mission_(TESS|K2)_
    pattern = re.compile(r'LK_exptime_(\w+)_LK_mission_(TESS|K2)_')

    txt_files = glob.glob(os.path.join(directory, '*.txt'))
    groups = {}

    for fpath in txt_files:
        filename = os.path.basename(fpath)

        match = pattern.search(filename)
        if match is None:
            # File doesn't match the expected pattern, skip
            continue
        
        exptime_val = match.group(1)
        mission = match.group(2)      # "TESS" or "K2"
        prefix5 = filename[:5]

        key = (prefix5, exptime_val, mission)
        if key not in groups:
            groups[key] = []
        groups[key].append(fpath)
        groups[key] = sorted(groups[key])
    
    return groups

def parse_sector_campaign_nums(file_list, mission):
    """
    Given a list of filenames (all guaranteed to be the same mission),
    extract the numeric sector(s) or campaign(s) from the substring:
      - If TESS: 'TESS_Sector_XX'
      - If K2:   'K2_Campaign_XX'

    Return a sorted list of the unique numbers found.
    """
    # For TESS, look for  'TESS_Sector_(\d+)'
    # For K2,   look for  'K2_Campaign_(\d+)'
    if mission == "TESS":
        pattern = re.compile(r'TESS_Sector_(\d+)')
    else:  # mission == "K2"
        pattern = re.compile(r'K2_Campaign_(\d+)')
    
    nums = set()
    for fpath in file_list:
        fname = os.path.basename(fpath)
        for m in pattern.finditer(fname):
            nums.add(int(m.group(1)))
    
    return sorted(nums)

def concatenate_and_fix_gaps(filepaths, gap_threshold=80.0):
    """
    Reads each .txt file (columns: time, flux) in filepaths,
    concatenates them, and fixes large time gaps > gap_threshold
    by shifting the left segments in a SINGLE pass for performance.

    Returns (time, flux) as numpy arrays.
    """
    all_time = []
    all_flux = []

    # 1) Read each file (skip the header line "0,1")
    for fpath in filepaths:
        data = np.genfromtxt(fpath, delimiter=',', skip_header=1)
        if data.size == 0:
            print('WARNING file {} empty'.format(fpath))
            continue
        all_time.append(data[:,0])
        all_flux.append(data[:,1])
    
    if not all_time:
        return np.array([]), np.array([])
    
    # 2) Concatenate
    time = np.concatenate(all_time)
    flux = np.concatenate(all_flux)

    # 3) Sort by time
    sort_idx = np.argsort(time)
    time = time[sort_idx]
    flux = flux[sort_idx]

    # 4) Compute median time step
    if len(time) > 1:
        dt_all = np.diff(time)
        median_dt = np.median(dt_all)
    else:
        median_dt = 0.0

    # 5) Identify all gap indices where gap > gap_threshold
    if len(time) > 1:
        dt = np.diff(time)
        gap_indices = np.where(dt > gap_threshold)[0]
    else:
        gap_indices = np.array([])

    if len(gap_indices) == 0:
        # No large gaps found
        is_shifted = False
        return time, flux, is_shifted

    # 6) Apply shifts to segments left of each gap in one pass
    total_shift = 0.0  # Track cumulative shift
    new_time = time.copy()  # Create a new array for modified time

    for i in gap_indices:
        gap_size = time[i+1] - time[i]
        if gap_size > gap_threshold:
            total_shift += gap_size + median_dt
            # Apply the total shift to all times up to index i
            new_time[:i+1] += total_shift
            is_shifted = True
    return new_time, flux, is_shifted

def main():
    directory = "/Users/creyes/Projects/harps/processed_lightcurves"
    new_directory = "/Users/creyes/Projects/harps/concatenated_lightcurves"
    gap_threshold = 80.0

    # 1) Group files by (prefix5, exptimeXXXX, mission)
    grouped_files = find_groups(directory)

    # 2) For each group, parse sector/campaign numbers, fix gaps, and write output
    for (prefix5, exptime_val, mission), file_list in grouped_files.items():
        if not file_list:
            continue

        # Get all sector/campaign numbers from these files
        sc_nums = parse_sector_campaign_nums(file_list, mission)  # sorted list

        # Concatenate & fix gaps
        final_time, final_flux, is_shifted = concatenate_and_fix_gaps(file_list, gap_threshold=gap_threshold)
        if len(final_time) == 0:
            print(f"No valid data for group ({prefix5}, {exptime_val}, {mission}), skipping.")
            continue

        # Build the "Sectors_XX_XX" or "Campaigns_XX_XX" string
        if mission == "TESS":
            # e.g. "Sectors_31_32_45"
            sc_string = "Sectors_" + "_".join(str(num) for num in sc_nums)
        else:  # mission == "K2"
            # e.g. "Campaigns_06_07"
            sc_string = "Campaigns_" + "_".join(str(num) for num in sc_nums)

        # Construct output filename
        if is_shifted:
            shifted_flag = 'IS_'
        else:
            shifted_flag = 'NOT_'

        out_name = (
            f"{prefix5}_LK_exptime_{exptime_val}_LK_mission_{sc_string}_{shifted_flag}SHIFTED_CONCATENATED.txt"
        )
        out_path = os.path.join(new_directory, out_name)

        # Save final data
        header_str = "TIME,FLUX"
        np.savetxt(
            out_path,
            np.column_stack([final_time, final_flux]),
            fmt="%.10f",
            delimiter=",",
            header=header_str,
            comments=""
        )

        print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
