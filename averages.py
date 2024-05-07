import pandas as pd
import os
import glob
from datetime import datetime

# Specify the folder path correctly
folder_path = 'input/Beachworks'

# List all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Initialize a list to store the averages
averages_list = []

def get_fips_name(file_basename, csv_path='data/FIPS.csv'):
    # Extract the FIPS code from the basename, assuming format "FIPS.csv"
    fips_code = file_basename.replace('.csv', '')
    
    # Load the CSV file
    fips_df = pd.read_csv(csv_path, sep=';')
    
    # Find the row with the matching FIPS Code
    match = fips_df.loc[fips_df['FIPS Code'] == fips_code, 'County Name']
    
    # Check if the search returned any results
    if match.empty:
        # Handle the case where no matching FIPS code was found
        return None  # Or, you could return a default value or raise a custom error
    else:
        # Return the County Name
        return match.values[0]

# Define the function to extract year from buildDate
def extract_year(date_str):
    if date_str in ['Unknown', '01-01-70', None, '']:
        return None
    try:
        date_obj = pd.to_datetime(date_str, errors='coerce')
        return date_obj.year if date_obj else None
    except ValueError:
        return None

# Define a function to filter extremes
def filter_extremes(column):
    lower_bound = column.quantile(0.1)
    upper_bound = column.quantile(0.8)
    return column[(column >= lower_bound) & (column <= upper_bound) & (column != 0)]

# Function to classify each value into a price range
def classify_into_range(value, price_ranges):
    if pd.isna(value) or value == 'Unknown':
        return 'Unknown'
    for i, (limit, label) in enumerate(price_ranges):
        if value == limit:
            return label
        if i == 0:
            continue
        if limit > value:
            return price_ranges[i-1][1]
    return price_ranges[-1][1]

# Define price ranges and labels
price_ranges = [
    (None, 'Unknown'),
    (0, '$0'),
    (1, '$1'),
    (25000, '$25,000'),
    (50000, '$50,000'),
    (100000, '$100,000'),
    (150000, '$150,000'),
    (200000, '$200,000'),
    (250000, '$250,000'),
    (300000, '$300,000'),
    (350000, '$350,000'),
    (400000, '$400,000'),
    (500000, '$500,000'),
    (600000, '$600,000'),
    (750000, '$750,000'),
    (1000000, '$1,000,000'),
    (1500000, '$1,500,000'),
    (2000000, '$2,000,000')
]

# Process each CSV file
for file_path in csv_files:
    # Load CSV with specified columns and filter for Use_Type == 'SFH'
    df = pd.read_csv(file_path, usecols=['LotSizeSqFt', 'totalValue', 'buildDate', 'SumLivingAreaSqFt', 'Use_Type'], dtype={'LotSizeSqFt': 'str', 'totalValue': 'str', 'buildDate': 'str', 'SumLivingAreaSqFt': 'str', 'Use_Type': 'str'})
    df = df[df['Use_Type'] == 'SFH']
    
    # Convert numeric columns, filtering out non-numeric values
    df['LotSizeSqFt'] = pd.to_numeric(df['LotSizeSqFt'], errors='coerce')
    df['totalValue'] = pd.to_numeric(df['totalValue'], errors='coerce')
    df['SumLivingAreaSqFt'] = pd.to_numeric(df['SumLivingAreaSqFt'], errors='coerce')
    
    # Apply filter extremes function
    df['LotSizeSqFt'] = filter_extremes(df['LotSizeSqFt'])
    df['totalValue'] = filter_extremes(df['totalValue'])
    df['SumLivingAreaSqFt'] = filter_extremes(df['SumLivingAreaSqFt'])
    
    # Convert 'buildDate' to 'buildYear'
    df['buildYear'] = df['buildDate'].apply(extract_year)
    
    # Calculate averages, excluding NaN values
    avg_lot_size_sq_ft = df['LotSizeSqFt'].mean(skipna=True)
    avg_total_value = df['totalValue'].mean(skipna=True)
    avg_sum_living_area_sq_ft = df['SumLivingAreaSqFt'].mean(skipna=True)
    avg_build_year = df['buildYear'].dropna().mean()  # Ensure to drop NaN before calculating mean
    
    # Append the averages as a tuple to the list
    averages_list.append((
        os.path.basename(file_path),
        avg_lot_size_sq_ft,
        avg_total_value,
        avg_sum_living_area_sq_ft,
        avg_build_year
    ))


# Create a DataFrame from the list of averages
averages_df = pd.DataFrame(averages_list, columns=['FileName', 'AvgLotSizeSqFt', 'AvgTotalValue', 'AvgSumLivingAreaSqFt', 'AvgBuildYear'])

# Display or save the final table of averages
print(averages_df)
# Optional: Save to a CSV file
# averages_df.to_csv('path/to/save/averages_table.csv', index=False)
