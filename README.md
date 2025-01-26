# LightcurveProcessor

LightcurveProcessor is a pipeline for advanced processing of astronomical lightcurves, including:
- Gap filling and sigma clipping.
- High-pass filtering for signal extraction.
- Concatenation of multiple lightcurves with gap correction.
- Metadata-based grouping and summarization.

## Features
1. Fill gaps up to 1.5 hours using linear interpolation.
2. Apply sigma clipping to remove outliers.
3. Normalize lightcurves using Gaussian filters.
4. Concatenate lightcurves of the same target and cadence, fixing gaps > 80 days.
5. Generate summary tables describing processed files.

## Usage
### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/LightcurveProcessor.git
   cd LightcurveProcessor
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
