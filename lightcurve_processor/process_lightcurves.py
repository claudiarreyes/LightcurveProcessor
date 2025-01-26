import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d

def process_lightcurve(file_path, output_dir, time_col='TIME', flux_col='PDCSAP_FLUX',
                       gap_threshold=1.5 / 24, sigma_clip=4, filter_window=10):
    """
    Process a lightcurve to handle gaps, apply sigma clipping, and normalize flux.

    Returns:
        str: Path to the processed lightcurve file.
    """
    # Load and preprocess
    lc = pd.read_csv(file_path, header=None, usecols=[0, 2], names=[time_col, flux_col], sep='\\s+')
    lc = lc.dropna(subset=[time_col, flux_col]).reset_index(drop=True)
    
    # Fill small gaps
    lc['time_diff'] = lc[time_col].diff()
    approx_time_step = lc[time_col].diff().median()
    gaps = lc[(lc['time_diff'] > approx_time_step) & (lc['time_diff'] < gap_threshold)]
    for idx in gaps.index:
        start_time, end_time = lc.loc[idx - 1, time_col], lc.loc[idx, time_col]
        new_times = np.arange(start_time + approx_time_step, end_time, approx_time_step)
        new_fluxes = np.interp(new_times, [start_time, end_time], [lc.loc[idx - 1, flux_col], lc.loc[idx, flux_col]])
        lc = pd.concat([lc, pd.DataFrame({time_col: new_times, flux_col: new_fluxes})]).sort_values(by=time_col)

    # Apply sigma clipping
    flux_median, flux_std = lc[flux_col].median(), lc[flux_col].std()
    lc = lc[(lc[flux_col] >= flux_median - sigma_clip * flux_std) & 
            (lc[flux_col] <= flux_median + sigma_clip * flux_std)]
    
    # Normalize using Gaussian filter
    lc['flux_normalized'] = gaussian_filter1d(lc[flux_col].values, sigma=filter_window)

    # Save processed lightcurve
    output_path = f"{output_dir}/{os.path.basename(file_path)}_processed.csv"
    lc.to_csv(output_path, index=False)
    return output_path
