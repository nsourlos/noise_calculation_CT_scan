# CT Scan Analysis Script

## Introduction
This Python [script](./noise_calculation_3D.py) is designed for the analysis of noise in CT scan data obtained from DICOM files. The script processes patient-specific DICOM files, extracts relevant information, performs 3D patch analysis on specific rectangle regions, and outputs noise values in Hounsfield Units (HU).

## Usage
1. **Input and Output Paths:**
   - Set the `data_path` variable to the directory containing patient-specific DICOM files (multiple folders, each with one patient)
   - Set the `output_path` variable to the desired output directory.

2. **Run the Script:**

   ```python noise_calculation_3D.py ```

## Script Overview

### Initial Setup:
- Imports necessary libraries and sets up input and output paths.
- Creates output directory if it doesn't exist.

### CT Files Extraction:
- Defines a function (`CT_files_extract`) to extract information from DICOM files.
- Utilizes parallel processing to extract data from all patient directories.

### Convert to Hounsfield Units (HU):
- Converts pixel data from DICOM files to Hounsfield Units (HU).

### Patch Analysis and Visualization:
- Processes each CT slice, performs patch analysis, and calculates HU values within specific rectangle region.
- Generates visualizations with bounding boxes around regions of interest.

### Analysis and Output:
- Outputs key metrics, such as average HU, mean noise, and more, to a text file (`output.txt`).
- Provides summary statistics and sorted noise values for participants.

## Notes:
- The script outputs results to the `output_path` directory, including visualizations and a text file.
- The script runtime can vary based on the dataset size.