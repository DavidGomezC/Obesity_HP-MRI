================================================================================
                    FAT MICE MRI - PROJECT README
                    MRI Dixon Image Processing Pipeline
================================================================================

OVERVIEW
--------
This project provides a pipeline for processing Dixon MRI images from mice,
specifically designed to:
  1. Split Dixon DICOM images into Fat and Water NIfTI components
  2. Compute MRI Proton Density Fat Fraction (MRIPDFF) maps
  3. Aggregate volume/segmentation statistics from multiple CSV exports coming from ITK-Snap
  4. Filter and extract organ-specific data (e.g., liver) for further analysis
  5. (Optional) Verify voxel spacing of NIfTI images to ensure correctness

The pipeline is intended to be run in sequence: preprocess DICOMs first,
then compute volumes with ITK-Snap, and finally filter and aggregate the results.


--------------------------------------------------------------------------------
ENVIRONMENT SETUP
--------------------------------------------------------------------------------

SETUP INSTRUCTIONS
------------------
  1. Create a new virtual environment:
       virtualenv --no-site-packages .venv

  2. Activate it:
       source .venv/bin/activate          (Linux/macOS)
       .venv\Scripts\activate             (Windows)

  3. Install all dependencies:
       pip install -r requirements.txt


--------------------------------------------------------------------------------
SCRIPTS - DETAILED DESCRIPTION & USAGE GUIDE
--------------------------------------------------------------------------------

========================================
1. Dicom_preprocessing.py
========================================

PURPOSE:
  Splits Dixon DICOM files (which interleave Fat and Water slices in a single
  volume) into three separate NIfTI outputs:
    - fat_{filename}.nii.gz      : Fat-only image
    - water_{filename}.nii.gz    : Water-only image
    - mripdff_{filename}.nii.gz  : Proton Density Fat Fraction map

HOW IT WORKS:
  Dixon MRI acquisition stores Fat slices in the first half of the volume and
  Water slices in the second half. The script:
    a) Reads each DICOM file in the input folder
    b) Splits the 3D array along the slice axis at the midpoint
    c) Reconstructs two separate SimpleITK images (Fat, Water), preserving
       the original origin, direction, and voxel spacing
    d) Saves Fat and Water as NIfTI files
    e) Reloads them with nibabel and computes:
         MRIPDFF = FAT / (FAT + WATER + epsilon)
       where epsilon = 1e-10 prevents division by zero
    f) Saves the MRIPDFF map as a NIfTI file

USAGE:
  python code/Dicom_preprocessing.py <input_folder> <output_folder>

  Arguments:
    input_folder   Path to a folder containing (one or many) .dcm Dixon DICOM files
    output_folder  Path to the folder where NIfTI outputs will be saved
                   (created automatically if it does not exist)

EXAMPLE:
  python code/Dicom_preprocessing.py ./dicom_data ./nifti_output

OUTPUT FILES (per input DICOM):
  fat_<original_name>.nii.gz
  water_<original_name>.nii.gz
  mripdff_<original_name>.nii.gz

NOTES:
  - Input DICOMs must have an even number of slices (Fat + Water interleaved)
  - Files that raise a ValueError during processing are skipped and reported
    at the end of the run
  - The original voxel spacing, origin, and direction are preserved in all
    output NIfTI files


========================================
2. Volume_computation.py
========================================

PURPOSE:
  Scans a folder of individual CSV files (one per image/subject, following ITK-Snap volume statistics output format ), 
  cleans column names, tags each row with its source image identifier, and merges everything into a single combined 
  CSV file for downstream analysis.

HOW IT WORKS:
    a) Iterates over all *.csv files in the input folder
    b) Strips unit annotations from column headers
       e.g., "Volume (mm^3)" becomes "Volume"
    c) Adds an "Image Identifier" column derived from the CSV filename
    d) Concatenates all individual dataframes into one combined CSV

USAGE:
  Edit the following variables at the bottom of the script before running:

    input_folder  = "path/to/folder/with/individual/csvs"
    output_folder = "path/to/save/combined.csv"

  Then run:
    python code/Volume_computation.py

OUTPUT:
  combined.csv  - Merged table with all subjects and a new
                  "Image Identifier" column

NOTES:
  - The script uses hardcoded paths; update input_folder and output_folder before use
  - Column names with parenthetical units are automatically cleaned
  - The combined CSV includes a row index column by default


========================================
3. dataframeFiltering.py
========================================
HOW IT WORKS:
    a) Reads combined.csv
    b) Filters rows where "Label Name" equals the target label ( Liver, Background, etc.). Works also with multiple labels 
    c) Selects a specific subset of columns by position
    d) Saves the filtered result to a new CSV (e.g., Liver.csv)

USAGE:
  Edit the following variables in the script before running:

    Path to combined.csv (line 3)
    Target label string  (line 5, default: "Label 1")
    Output CSV path      (last line, default: Liver.csv)

  Then run:
    python code/dataframeFiltering.py

OUTPUT:
  Liver.csv  (or your chosen output name) - Filtered organ-level statistics

NOTES:
  - Column selection uses positional indexing (iloc); adjust indices if your
    CSV structure differs
  - The script contains commented-out lines for manual value correction of
    a specific subject (image ID "15518-2_15518"); uncomment and adapt
    these if you need to patch individual rows


========================================
4. check_voxel_size.py
========================================

PURPOSE:
  Quick utility to inspect the voxel spacing (x, y, z in mm) of any NIfTI
  image and print the volume of a single voxel in mm^3.

HOW IT WORKS:
  Reads a NIfTI file using SimpleITK, retrieves the spacing tuple, and
  computes: voxel_volume = spacing_x * spacing_y * spacing_z

USAGE:
  Edit the image path on line 4, then run:
    python code/check_voxel_size.py

  Expected output:
    0.XXXXXX   (voxel volume in mm^3)

NOTES:
  - Useful for verifying that preprocessing preserved the correct voxel
    dimensions before running volumetric analysis
  - Works with any SimpleITK-readable format (NIfTI, DICOM, MHA, etc.)


--------------------------------------------------------------------------------
RECOMMENDED USAGE
--------------------------------------------------------------------------------

  STEP 1 — Preprocess DICOMs
    python code/Dicom_preprocessing.py ./raw_dicoms ./nifti_output
    
    Output: fat_*.nii.gz, water_*.nii.gz, mripdff_*.nii.gz for each subject

  STEP 2 — (Optional) Verify voxel sizes
    Edit check_voxel_size.py with one output path, then:
    python code/check_voxel_size.py
    
    Confirm spacing is as expected before proceeding.

  STEP 3 — Segmentation in ITK-SNAP
    a) Open the water image (water_*.nii.gz) in ITK-SNAP as the main image.
    b) Perform organ segmentation on the water image (better soft-tissue
       contrast makes it easier to delineate structures such as the liver).
    c) Save the segmentation.
    d) Load the fat image (fat_*.nii.gz) as the main image in ITK-Snap
    
    e) Import/apply the segmentation saved in step (c) onto the fat
       image using: Segmentation > Load Segmentation.
    f) Check and optionally refine the segmentation on the fat image.
    g) Load the MRIPDFF image (mripdff_*.nii.gz) as
       the main image.
    h) Import/apply the segmentation saved in step (c-f) onto the MRIPDFF
       image using: Segmentation > Load Segmentation.
    i) Export per-subject statistics (volumes, intensities) as individual
       CSV files into a single folder.

  STEP 4 — Aggregate statistics
    Edit input_folder and output_folder in Volume_computation.py, then:
    python code/Volume_computation.py
    
    Output: combined.csv

  STEP 5 — Filter by organ
    Edit paths and label name in dataframeFiltering.py, then:
    python code/dataframeFiltering.py
    
    Output: Liver.csv
