# Tool for splitting the Dixon DICOM (Fat and Water images) into two 
# separate nifti
import SimpleITK as sitk
from pathlib import Path
import os, sys
import nibabel as nib
import numpy as np


def get_filename_without_extension(file_path):
    """
    Extracts the filename from a given file path, excluding the file extension.

    Args:
        file_path (str): The path to the file from which to extract the filename.

    Returns:
        str: The filename without its extension.
    
    Example:
        >>> get_filename_without_extension('/path/to/file.txt')
        'file'
    """
    file_basename = os.path.basename(file_path)
    filename_without_extension = file_basename.split('.')[0]
    return filename_without_extension

def split_images(input_img,output_folder):
    """
    Splits a DICOM image into fat and water components, computes the MRIPDFF image, 
    and saves all images in the specified output folder.

    The function separates the first half number of slices of the input image as the fat array and the 
    remaining slices as the water array. Then, it creates two separate images from these arrays. 
    It calculates the MRI Proton Density Fat Fraction (MRIPDFF) by dividing the fat array by 
    the sum of the fat and water arrays. Finally, it saves the fat, water, and MRIPDFF images 
    in NIfTI format (.nii.gz).

    Args:
        input_img (str): The file path of the DICOM image to be processed.
        output_folder (str): The folder where the output fat, water, and MRIPDFF images will be saved.

    Outputs:
        - fat_{filename}.nii.gz: Image containing the fat component.
        - water_{filename}.nii.gz: Image containing the water component.
        - mripdff_{filename}.nii.gz: Image containing the MRIPDFF component.

    Example:
        >>> split_images('/path/to/dicom/image.dcm', '/output/folder')

    Notes:
        - The input image is expected to have an even number slices, with the first half corresponding 
          to fat and the rest to water.
        - The MRIPDFF image is calculated as: MRIPDFF = FAT / (FAT + WATER).
    """
    
    #Load image, pixel array and metadata info
    image = sitk.ReadImage(input_img)
    array = sitk.GetArrayFromImage(image)
    origin = image.GetOrigin()
    direction = image.GetDirection()
    spacing = image.GetSpacing()

    #original filename of the image
    filename = get_filename_without_extension(input_img)

    #Check dimensionality of image
    

    split_point = int(array.shape[0] / 2) # assuming first half contains fat and second half contains water
    

    #Separate Fat and Water arrays
    FAT_ARRAY = array[0:split_point,:,:]
    WATER_ARRAY = array[split_point:,:,:]

    print(f"Image:{filename}|fat_size:{FAT_ARRAY.shape[0]}|water_size:{WATER_ARRAY.shape[0]}")
    #Create Fat Image
    FAT = sitk.GetImageFromArray(FAT_ARRAY)
    FAT.SetDirection(direction)
    FAT.SetOrigin(origin)
    FAT.SetSpacing(spacing)

    #Create Water Image
    WATER = sitk.GetImageFromArray(WATER_ARRAY)
    WATER.SetDirection(direction)
    WATER.SetOrigin(origin)
    WATER.SetSpacing(spacing)

    #Create the output folder if it does not exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    #Save Fat and Water images in output folder
    sitk.WriteImage(FAT,f"{output_folder}/fat_{filename}.nii.gz")
    sitk.WriteImage(WATER,f"{output_folder}/water_{filename}.nii.gz")

    #MRIPDFF Image using nibabel

    #Load fat and water images
    FAT_NII = nib.load(f"{output_folder}/fat_{filename}.nii.gz")
    WATER_NII = nib.load(f"{output_folder}/water_{filename}.nii.gz")

    #Access numpy arrays
    FAT_ARRAY = FAT_NII.get_fdata()
    WATER_ARRAY = WATER_NII.get_fdata()

    #Compute the MRIPDFF Array (adding epsilon to avoid zero division)
    epsilon = 1e-10
    MRIPDFF_ARRAY = FAT_ARRAY/(FAT_ARRAY + WATER_ARRAY + epsilon)

    #Create a new image from the MRIPDFF ARRAY
    MRIPDFF = nib.Nifti1Image(MRIPDFF_ARRAY, FAT_NII.affine)

    #Save the MRIPDFF Image

    nib.save(MRIPDFF, f"{output_folder}/mripdff_{filename}.nii.gz")

#Usage python Dicom_preprocessing.py inputfolder outputfolder
if __name__ == "__main__":
    
    #Check the number arguments and print usage info otherwise
    if(len(sys.argv)<3):
        print("Tool for splitting DIXON images:")
        print("Usage python Dicom_preprocessing.py input_folder output_folder")
        sys.exit(0)

    #Get input and output folder from command line argumnets
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    not_processed = []
    #Process each dicom in the folder    
    for dicom_file in Path(input_folder).glob('*.dcm'):

        try:
            split_images(dicom_file,output_folder)
            print(f"Processed: {dicom_file}")
        except ValueError:
            not_processed.append(dicom_file)
            continue
    if len(not_processed)>0:
        print("Some error occured with ID:")
        print(not_processed)
    print("End of program")
    #path = "input_img/02276-5_02276_High_resolution_E5_P1_EnIm1.dcm"
    #split_images(path,"/home/andrea/Scrivania/Splitted")