import os
from glob import glob
import csv


def parse_filename_metadata(filename):
    """
    Parse metadata from the filename based on its naming convention.

    Args:
        filename (str): The filename to parse.

    Returns:
        dict: A dictionary containing parsed metadata (`irow`, `tel_target`, `exptime`, `mission`).
    """
    metadata = {'irow': None, 'tel_target': None, 'exptime': None, 'mission': None}

    # Extract the first 5 characters as irow
    metadata['irow'] = filename[:5]

    # Extract tel_target
    try:
        start_idx = filename.index("target_") + len("target_")
        end_idx = filename.index("_LK_targetname", start_idx)
        metadata['tel_target'] = filename[start_idx:end_idx]
    except ValueError:
        metadata['tel_target'] = None

    # Extract exptime
    try:
        start_exp = filename.index("LK_exptime_") + len("LK_exptime_")
        end_exp = filename.index("_LK_mission", start_exp)
        metadata['exptime'] = filename[start_exp:end_exp]
    except ValueError:
        metadata['exptime'] = None

    # Extract mission
    try:
        start_mission = filename.index("LK_mission_") + len("LK_mission_")
        end_mission = filename.index("_LK_author", start_mission)
        metadata['mission'] = filename[start_mission:end_mission]
    except ValueError:
        metadata['mission'] = None

    return metadata


def collect_metadata(directory):
    """
    Collect metadata from all lightcurve files in the directory.

    Args:
        directory (str): Directory containing the lightcurve files.

    Returns:
        dict: A dictionary where keys are `irow` and values are metadata dictionaries.
    """
    metadata_dict = {}

    # Get all files in the directory
    for file_path in sorted(glob(os.path.join(directory, "*.txt"))):
        filename = os.path.basename(file_path)
        metadata = parse_filename_metadata(filename)

        # Group metadata by `irow`
        irow = metadata['irow']
        if irow not in metadata_dict:
            metadata_dict[irow] = {'tel_target': metadata['tel_target'], 'exptime': {}}

        exptime = metadata['exptime']
        mission = metadata['mission']

        if exptime and mission:
            metadata_dict[irow]['exptime'].setdefault(exptime, []).append(mission)

    return metadata_dict


def write_summary_csv(metadata_dict, output_file):
    """
    Write metadata summary to a CSV file.

    Args:
        metadata_dict (dict): Dictionary containing metadata grouped by `irow`.
        output_file (str): Path to save the summary CSV.
    """
    # Collect all unique exposure times across all `irow`
    all_exptimes = sorted(
        {exptime for data in metadata_dict.values() for exptime in data['exptime']}
    )

    # Write the metadata to a CSV file
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Header
        header = ["irow", "tel_target"] + all_exptimes
        writer.writerow(header)

        # Rows
        for irow, data in sorted(metadata_dict.items()):
            row = [irow, data['tel_target']]
            for exptime in all_exptimes:
                if exptime in data['exptime']:
                    missions = data['exptime'][exptime]
                    row.append(",".join(missions))
                else:
                    row.append("NO")
            writer.writerow(row)

    print(f"Summary saved to: {output_file}")


def main(directory, output_file):
    """
    Main function to describe files in a directory and save a summary CSV.

    Args:
        directory (str): Directory containing lightcurve files.
        output_file (str): Path to save the summary CSV.
    """
    metadata_dict = collect_metadata(directory)
    write_summary_csv(metadata_dict, output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a summary CSV of lightcurve files.")
    parser.add_argument("directory", type=str, help="Directory containing lightcurve files.")
    parser.add_argument("output_file", type=str, help="Path to save the summary CSV.")
    args = parser.parse_args()

    main(args.directory, args.output_file)
