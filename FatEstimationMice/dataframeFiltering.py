import pandas as pd

combined_df = pd.read_csv("/home/andrea/Scrivania/combined.csv")

selected_df = combined_df.loc[combined_df['Label Name']== "Label 1"]
filtered = selected_df.iloc[:,[7,3,4,5,6]]
#filtered.iloc[29,[3,4,5,6]] = (74439,74439.0,0.3274,0.1818)
#print(filtered.loc[filtered['Image Identifier']=="15518-2_15518",[3,4,5,6]])
#print(filtered)

#filtered['Image Identifier']=="15518-2_15518"

#print(filtered['Image Identifier']=="15518-2_15518")
filtered.iloc[filtered['Image Identifier']=="15518-2_15518",[1,2,3,4]]=(74439,74439.0,0.3274,0.1818)
filtered.to_csv('/home/andrea/Scrivania/Liver.csv',index=False)