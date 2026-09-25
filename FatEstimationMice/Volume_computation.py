import pandas as pd
from pathlib import Path
import re
import os

def modify_csv(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Get the image identifier from the filename (without the extension)
    image_identifier = os.path.splitext(os.path.basename(file_path))[0]

    # Rename columns by removing any parentheses (but keeping valid units like mm^3)
    new_columns = {col: re.sub(r' \([^)]+\)', '', col) for col in df.columns}
    df.rename(columns=new_columns, inplace=True)

    # Add a new column to store the image identifier
    df['Image Identifier'] = image_identifier

    # Save the modified CSV file
    modified_file_path = f'modified_{os.path.basename(file_path)}'

    return df
    

input_folder = "E:/Documents/Projects/W - Fat Mice MRI/output"
output_folder = "."

print("producing the full csv file from individual ones")

dataframes = []
for csv_file in Path(input_folder).glob('*.csv'):
    df = modify_csv(csv_file)
    dataframes.append(df)

combined_df = pd.concat(dataframes,ignore_index=True)
combined_df.to_csv(output_folder+'/combined.csv',index=True)     
 
#Selecting Liver only 

print("End of program")