import os
import pandas as pd

# Folder where your CSVs are stored
folder_path = r'Z:\PO Fundamental\MPOB Data\BTS_district'

# Mapping Malay month names in filenames to formatted date strings
month_map = {
    "jan": "Jan-25",
    "feb": "Feb-25",
    "mac": "Mar-25",
    "apr": "Apr-25",
    "mei": "May-25",
    "jun": "Jun-25",
    "jul": "Jul-25",
    "ogo": "Aug-25",
    "sep": "Sep-25",
    "okt": "Oct-25",
    "nov": "Nov-25",
    "dis": "Dec-25"
}

# List to store filtered DataFrames
filtered_dfs = []

# Loop through all files in folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv') and file_name.startswith('2025'):  # only 2025 onwards
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)
        
        # Filter for kod_negeri = 13 only
        df_filtered = df[df['kod_negeri'] == 13].copy()
        
        # Extract the Malay month from filename (assuming filename like '2025jan.csv')
        file_month = file_name[4:7].lower()  # 4th,5th,6th chars
        date_str = month_map.get(file_month, "")  # map to date
        
        # Add date as the first column
        df_filtered.insert(0, 'date', date_str)
        
        filtered_dfs.append(df_filtered)

# Combine all filtered data into one DataFrame
combined_df = pd.concat(filtered_dfs, ignore_index=True)

# Save combined data to CSV
output_file = os.path.join(folder_path, 'combined_kod_negeri_13_2025_onwards.csv')
combined_df.to_csv(output_file, index=False)

print(f"Combined data saved to: {output_file}")
