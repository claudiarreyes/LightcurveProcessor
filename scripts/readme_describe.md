## What This Script Does

1. Parses Metadata:
* Extracts irow, tel_target, exptime, and mission from the filenames using consistent patterns.

2. Groups Metadata by irow:
* Organizes files by their unique irow identifier and groups missions by exposure time.

3. Generates a Summary Table:
* Writes a CSV where:
  * Each row represents an irow.
  * Columns include irow, tel_target, and one column per unique exposure time.
  * Cells list missions corresponding to each exposure time or "NO" if no data is available.


## Example Input and Output
### Example Filenames:
```
00001_target_StarA_LK_exptime_120_LK_mission_TESS_LK_author.txt
00001_target_StarA_LK_exptime_120_LK_mission_K2_LK_author.txt
00002_target_StarB_LK_exptime_60_LK_mission_TESS_LK_author.txt
00003_target_StarC_LK_exptime_120_LK_mission_TESS_LK_author.txt
```

Resulting CSV (describe_files_per_irow.csv):
```
irow,tel_target,60,120
00001,StarA,NO,TESS,K2
00002,StarB,TESS,NO
00003,StarC,NO,TESS
```

## Command-Line Usage

1. Run the script to generate the summary:

```
scripts/describe_files.py /path/to/lightcurve/files /path/to/output/summary.csv
```

2. Arguments:

  * directory: Path to the directory containing lightcurve files.
  * output_file: Path to save the generated summary CSV.
