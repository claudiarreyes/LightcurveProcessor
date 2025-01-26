import os
import numpy as np
from astropy.timeseries import LombScargle
import pandas as pd

def define_paths():
    """Define input and output paths."""
    input_path = '/Users/creyes/Projects/harps/concatenated_lightcurves'
    output_path = '/Users/creyes/Projects/harps/psd'

    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    return input_path, output_path

def psd(file, input_path, cadence, rgb):
    """Compute the Power Spectral Density (PSD) of the given file."""
    # Determine max frequency based on cadence and RGB classification
    if rgb == 'RGB_CMD':
        if cadence == 1800:
            max_freq = 280
        elif cadence in [60, 120]:
            max_freq = 900
        elif cadence == 20:
            max_freq = 4000
        else:
            raise ValueError("Unsupported cadence for RGB_CMD")
    else:
        if cadence <= 120:
            max_freq = 4000
        else:
            max_freq = 280

    # Read the input file
    filepath = os.path.join(input_path, file)
    q = np.loadtxt(filepath, delimiter=',', skiprows=1)

    # Remove rows with NaNs in any column
    q = q[~np.isnan(q).any(axis=1)]

    # Extract time and flux columns
    t = q[:, 0]  # Time
    f = q[:, 1]  # Flux
    f *=1e6
    
    # Convert time to days
    t *= 0.0864

    # Replace NaNs in flux with zero (if any)
    f = np.nan_to_num(f, nan=0)

    # Calculate variance of flux
    var = ((f - f.mean()) ** 2).sum() / (len(f) - 1)

    # Compute Lomb-Scargle periodogram
    dt = np.diff(t)
    mean_dt = np.mean(dt)
    median_dt = np.median(dt)

    freq, power = LombScargle(t, f).autopower(
        nyquist_factor=(mean_dt / median_dt),
        normalization='psd',
        samples_per_peak=10,
        maximum_frequency=max_freq
    )

    # Normalize power (flux in ppm -> power in ppm^2/uHz)
    power = (2 * power * var) / ((np.sum(power)) * (freq[1] - freq[0]))

    return freq, power

def main():
    """Main function to process all files and compute PSD."""
    input_path, output_path = define_paths()

    df = pd.read_csv('/Users/creyes/Projects/harps/df_lightcurves_describe.csv')
    # Iterate through all files
    for _, file in df.iterrows():
        if file['file_name'].endswith('.txt'):  # Process only CSV files

            # Create an appropriate name for the output file
            base_name = os.path.splitext(file['file_name'])[0]  # Remove the .csv extension
            output_file = os.path.join(output_path, f"{base_name}_psd.csv")

            # Check if the output file already exists
            if os.path.exists(output_file):
                print(f"Output already exists for {file['file_name']}, skipping.")
                continue  # Skip processing if the output file exists

            # Set cadence and RGB flag (you can customize how these values are determined)
            cadence = file['cadence']  # Example cadence value
            rgb = file['RGB']  # Example RGB flag (can also be dynamically set per file)

            try:
                print(f"Processing file: {file['file_name']}")
                freq, power = psd(file['file_name'], input_path, cadence, rgb)

                # Save the PSD data to the output file
                header = 'Frequency,Power'
                np.savetxt(output_file, np.column_stack((freq, power)), delimiter=',', header=header, comments='')
                print(f"Saved PSD data to: {output_file}")

            except ValueError as e:
                print(f"Error processing {file['file_name']}: {e}")
                break

if __name__ == "__main__":
    main()
