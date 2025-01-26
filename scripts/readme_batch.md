## What the Script Does
1. Processes Individual Lightcurves:

* Calls process_lightcurve for each .txt file in the input_dir.
* Applies gap filling, sigma clipping, and Gaussian filtering to each lightcurve.
* Saves processed lightcurves in the processed/ subdirectory of the output_dir.

2. Groups Lightcurves by Metadata:

* Uses group_files_by_metadata to group files based on prefix5, exptime, and mission.
Concatenates Lightcurves by Group:

3. Calls concatenate_and_fix_gaps for each group of files.
* Fixes large gaps (>80 days by default) between segments in the same group.
* Saves concatenated files in the concatenated/ subdirectory of the output_dir.

4. Command-Line Arguments:

* Users can specify:
  * --gap_threshold: Maximum gap to fill in individual lightcurves.
  * --sigma_clip: Sigma threshold for outlier removal.
  * --filter_window: Gaussian filter window size.
  * --concatenate_gaps: Threshold for fixing large gaps in concatenation.

## Example Usage
```
# Batch process lightcurves with default parameters
python scripts/process_batch.py /path/to/input_dir /path/to/output_dir

# Customize parameters
python scripts/process_batch.py /path/to/input_dir /path/to/output_dir \
    --gap_threshold 0.08 \
    --sigma_clip 5 \
    --filter_window 15 \
    --concatenate_gaps 100
```
