# LightcurveProcessor

=== NOT READY TO USE ===

LightcurveProcessor is a pipeline for advanced processing of astronomical lightcurves, including:
- Gap filling and sigma clipping.
- High-pass filtering for signal extraction.
- Concatenation of multiple lightcurves with gap correction.
- Metadata-based grouping and summarization.

This repository contains a set of scripts to process, organize, and summarize astronomical lightcurves.

## Features
- **`process_lightcurves.py`**: Handles gap filling, sigma clipping, high-pass filtering, and normalization of lightcurves.
- **`group_and_concatenate.py`**: Groups lightcurve files by metadata and concatenates them while fixing large gaps.
- **`describe_files.py`**: Generates a summary table describing available lightcurve files.

## Usage

### 1. Clone the repository
Clone the repository to your local machine and navigate to the directory:
```bash
git clone https://github.com/yourusername/LightcurveProcessor.git
cd LightcurveProcessor
```

### 2. Install dependencies
Install the required Python libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Run the scripts

#### Process lightcurves
Run the script to process lightcurve files (gap filling, sigma clipping, normalization):
```bash
python scripts/process_lightcurves.py <input_dir> <output_dir>
```
Replace `<input_dir>` with the directory containing raw lightcurve files and `<output_dir>` with the directory to save processed lightcurve files.

#### Group and concatenate lightcurves
Group lightcurve files by metadata and concatenate them:
```bash
python scripts/group_and_concatenate.py
```

#### Describe lightcurve files
Generate a summary CSV describing all available lightcurve files:
```bash
python scripts/describe_files.py <directory> <output_file>
```
Replace `<directory>` with the path to your lightcurve files and `<output_file>` with the desired path for the summary CSV.

## Requirements
The following Python libraries are required to run the scripts:
- `numpy`
- `pandas`
- `scipy`
- `astropy`
```

## License
This project is licensed under the [MIT License](LICENSE).

