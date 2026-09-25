import SimpleITK as sitk

# read image
im = sitk.ReadImage("/home/andrea/Scrivania/W - Fat Mice MRI/output/fat_02276-5_02276_High_resolution_E5_P1_EnIm1.nii.gz")

# get voxel spacing (for 3-D image)
spacing = im.GetSpacing()
spacing_x = spacing[0]
spacing_y = spacing[1]
spacing_z = spacing[2]

# determine volume of a single voxel
voxel_volume = spacing_x * spacing_y * spacing_z
print(voxel_volume)