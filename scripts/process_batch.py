import os
import argparse
from lightcurve_processor.process_lightcurves import process_lightcurve
from lightcurve_processor.group_and_concatenate import group_files_by_metadata, concatenate_and_fix_gaps

def process_batch(input_dir, output_dir, gap_threshold=1.5 / 24, sigma_clip=4, filter_window=10, concatenate_gaps=80):
    """
    Batch process lightcurve files:
    1. Process individual lightcurve files (gap filling, sigma clipping, filtering).
    2. Group files by metadata and concatenate them, fixing large gaps.
    
    Args:
        input_dir (str): Directory containing raw lightcurve files.
        output_dir (str): Directory to save processed lightcurve files.
        gap_threshold (float): Maximum gap (in days) to fill in individual lightcurves.
        sigma_clip (float): Sigma threshold for clipping outliers.
        filter_window (float): Window size for Gaussian filtering in days.
        concatenate_gaps (float): Threshold for fixing large gaps during concatenation.

    Returns:
        None
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Process each lightcurve individually
    print("Processing individual lightcurves...")
    processed_dir = os.path.join(output_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            file_path = os.path.join(input_dir, file)
            print(f"Processing: {file}")
            try:
                process_lightcurve(
                    file_path, 
                    processed_dir, 
                    gap_threshold=gap_threshold, 
                    sigma_clip=sigma_clip, 
                    filter_window=filter_window
                )
            except Exception as e:
                print(f"Error processing {file}: {e}")

    # Step 2: Group files and concatenate
    print("Grouping and concatenating lightcurves...")
    concatenated_dir = os.path.join(output_dir, "concatenated")
    os.makedirs(concatenated_dir, exist_ok=True)
    grouped_files = group_files_by_metadata(processed_dir)

    for group, file_list in grouped_files.items():
        prefix5, exptime, mission = group
        print(f"Concatenating group: {group} ({len(file_list)} files)")
        try:
            time, flux = concatenate_and_fix_gaps(file_list, gap_threshold=concatenate_gaps)
            if len(time) > 0:
                output_file = os.path.join(
                    concatenated_dir, f"{prefix5}_LK_exptime_{exptime}_LK_mission_{mission}_CONCATENATED.txt"
                )
                header = "TIME,FLUX"
                np.savetxt(output_file, np.column_stack((time, flux)), delimiter=",", header=header, comments="")
                print(f"Saved concatenated file: {output_file}")
            else:
                print(f"No valid data for group: {group}")
        except Exception as e:
            print(f"Error concatenating group {group}: {e}")

    print("Batch processing complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process lightcurves with gap filling, filtering, and concatenation.")
    parser.add_argument("input_dir", type=str, help="Directory containing raw lightcurve files.")
    parser.add_argument("output_dir", type=str, help="Directory to save processed lightcurve files.")
    parser.add_argument("--gap_threshold", type=float, default=1.5 / 24, help="Gap threshold in days for individual lightcurves. Default: 1.5 hours.")
    parser.add_argument("--sigma_clip", type=float, default=4, help="Sigma threshold for clipping outliers. Default: 4.")
    parser.add_argument("--filter_window", type=float, default=10, help="Window size for Gaussian filtering in days. Default: 10.")
    parser.add_argument("--concatenate_gaps", type=float, default=80, help="Gap threshold in days for concatenation. Default: 80 days.")

    args = parser.parse_args()

    process_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        gap_threshold=args.gap_threshold,
        sigma_clip=args.sigma_clip,
        filter_window=args.filter_window,
        concatenate_gaps=args.concatenate_gaps
    )
