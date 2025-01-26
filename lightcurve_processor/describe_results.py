import os
from glob import glob
import csv

def main(output_dir = '/Users/creyes/Projects/harps/lightcurves/'):
    
    # Dictionary to store data in the form:
    # data[irow] = {
    #     'tel_target': some_string_or_None,
    #     'exptime': {
    #         exptime_code: [list_of_mission_info_strings]
    #     }
    # }
    data = {}

    # Read all files in the directory
    for file_path in sorted(glob(os.path.join(output_dir, "*"))):
        filename = os.path.basename(file_path)

        # Extract the first 5 characters as irow
        irow = filename[:5]

        # Ensure we have an entry for this irow
        if irow not in data:
            data[irow] = {
                "tel_target": None,
                "exptime": {}
            }

        # ----------------------------------------------------------------------
        # 1) Optional: Parse tel_target (between "target_" and "_LK_targetname")
        # ----------------------------------------------------------------------
        try:
            start_idx = filename.index("target_") + len("target_")
            end_idx = filename.index("_LK_targetname", start_idx)
            tel_target = filename[start_idx:end_idx]
            # Store or overwrite tel_target (assuming it's the same for a given irow)
            data[irow]["tel_target"] = tel_target
        except ValueError:
            # If the pattern doesn't exist in the filename, ignore
            pass

        # ----------------------------------------------------------------------
        # 2) Parse the exptime code (between "LK_exptime_" and "_LK_mission")
        # ----------------------------------------------------------------------
        exptime_code = None
        try:
            start_exp = filename.index("LK_exptime_") + len("LK_exptime_")
            end_exp = filename.index("_LK_mission", start_exp)
            exptime_code = filename[start_exp:end_exp]
        except ValueError:
            # If "LK_exptime_" or "_LK_mission" not found, skip
            pass

        # If we found an exptime_code, parse mission_info
        if exptime_code:
            try:
                start_mis = filename.index("LK_mission_") + len("LK_mission_")
                end_mis = filename.index("_LK_author", start_mis)
                mission_info = filename[start_mis:end_mis]
            except ValueError:
                # If "LK_mission_" or "_LK_author" not found, skip
                mission_info = None

            # Add mission_info to our data structure
            if mission_info:
                data[irow]["exptime"].setdefault(exptime_code, []).append(mission_info)

    # --------------------------------------------------------------------------
    # Collect all unique exptime codes across all irows
    # --------------------------------------------------------------------------
    all_exptimes = set()
    for irow, info in data.items():
        for code in info["exptime"].keys():
            all_exptimes.add(code)

    # Sort exptime codes so columns are in a consistent order
    all_exptimes = sorted(all_exptimes)

    # --------------------------------------------------------------------------
    # Write the data to a CSV
    # Columns: irow, tel_target, then one column per exptime code
    # --------------------------------------------------------------------------
    with open("describe_files_per_irow.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Create the header
        header = ["irow", "tel_target"] + all_exptimes
        writer.writerow(header)

        # Sort rows by irow so output is consistent
        for irow in sorted(data.keys()):
            row_data = data[irow]
            tel_target = row_data["tel_target"]

            row = [irow, tel_target]

            # For each exptime code, add either the list of mission_info or False
            for code in all_exptimes:
                if code in row_data["exptime"]:
                    # Convert the mission_info list to a comma-separated string
                    mission_list = row_data["exptime"][code]
                    row.append(",".join(mission_list))
                else:
                    row.append("NO")

            writer.writerow(row)

if __name__ == "__main__":
    main()
