import pandas as pd
import numpy as np


def process_lightcurve(file_path, output_dir, time_col='TIME', flux_col='PDCSAP_FLUX',
                       gap_threshold=1.5 / 24, sigma_clip=4, filter_window=10):
    """
    Process a lightcurve to:
    1. Remove rows with NaNs in flux at the beginning or end of the lightcurve.
    2. Fill gaps smaller than 1.5 hours using linear interpolation.
    3. Drop rows if the NaN gaps are larger than 1.5 hours.
    4. Apply 5-sigma clipping to remove flux outliers.
    5. Normalize flux using a Gaussian filter to remove low-frequency signals.

    Parameters:
        file_path (str): Path to the lightcurve CSV file.
        output_dir (str): Directory to save the processed lightcurve.
        time_col (str): Name of the time column. Default is 'TIME'.
        flux_col (str): Name of the flux column. Default is 'PDCSAP_FLUX'.
        gap_threshold (float): Gap threshold in days (default is 1.5 hours).
        sigma_clip (float): Sigma threshold for clipping outliers.
        filter_window (float): Window size for the Gaussian filter in days.

    Returns:
        str: Path to the processed lightcurve file.
    """
    # Load the light curve data
    lc = pd.read_csv(file_path, header=None, usecols=[0, 2], names=[time_col, flux_col], sep='\\s+')

    # Remove rows with NaNs in 'TIME' or 'PDCSAP_FLUX' at the beginning or end
    lc = lc.dropna(subset=[time_col, flux_col]).reset_index(drop=True)
    lc_clean = lc.copy()

    # Calculate time differences between consecutive observations
    lc['time_diff'] = lc[time_col].diff()

    #############################################
    # Define a function to interpolate small gaps
    approx_time_step = lc[time_col].diff().median()

    # Identify gaps larger than the threshold
    gaps = lc[((approx_time_step*1.95) < lc['time_diff']) & (lc['time_diff'] < gap_threshold)]

    # Initialize the output DataFrame
    filled_lc = lc.copy()

    #  Iterate over each gap and fill it
    for idx in gaps.index:
        # Start and end of the gap
        start_time = lc.loc[idx - 1, time_col]
        end_time = lc.loc[idx, time_col]
        start_flux = lc.loc[idx - 1, flux_col]
        end_flux = lc.loc[idx, flux_col]
        
        # Generate new time points within the gap
        new_times = np.arange(start_time + approx_time_step, end_time, approx_time_step)
        if len(new_times) > 0:
            # Linearly interpolate flux values for the new times
            new_fluxes = np.interp(new_times, [start_time, end_time], [start_flux, end_flux])
            
            # Create a DataFrame for the new points
            new_points = pd.DataFrame({time_col: new_times, flux_col: new_fluxes})
            
            # Insert the new points into the DataFrame
            filled_lc = pd.concat([filled_lc, new_points]).sort_values(by=time_col).reset_index(drop=True)

    # Drop the time_diff column and display the result
    filled_lc = filled_lc.drop(columns=['time_diff'])


    # Apply 4-sigma clipping
    flux_median = filled_lc['PDCSAP_FLUX'].median()
    flux_std = filled_lc['PDCSAP_FLUX'].std()
    filled_lc = filled_lc[(filled_lc['PDCSAP_FLUX'] >= flux_median - sigma_clip * flux_std) & (filled_lc['PDCSAP_FLUX'] <= flux_median + sigma_clip * flux_std)]

    t = filled_lc[time_col].values
    f = filled_lc[flux_col].values

    # Define the width of the window for local normalization
    width = 10  # Adjust this value as needed

    # Initialize an array to store the normalized flux
    f_normalized = np.full_like(f, np.nan)

    # Perform local normalization using vectorized operations
    for j in range(len(t)):
        if not np.isnan(f[j]):
            # Determine the window of indices within the specified width
            mask = np.abs(t - t[j]) <= width
            if np.any(mask):
                f_normalized[j] = f[j] / np.nanmedian(f[mask])

    # Second normalization
    f_double_normalized = np.full_like(f_normalized, np.nan)
    for j in range(len(t)):
        if not np.isnan(f_normalized[j]):
            # Determine the window of indices within the specified width
            mask = np.abs(t - t[j]) <= width
            if np.any(mask):
                f_double_normalized[j] = f_normalized[j] / np.nanmedian(f_normalized[mask])

    # Combine the time and double-normalized flux into a single array
    result = np.column_stack((t, f_double_normalized))

    # Save the processed lightcurve
    original_name = os.path.basename(file_path)
    new_name = f"{original_name[:6]}fill_sigclip_hipass_{original_name[6:]}"
    output_path = os.path.join(output_dir, new_name)
    pd.DataFrame(result).to_csv(output_path, index=False)

    return output_path
