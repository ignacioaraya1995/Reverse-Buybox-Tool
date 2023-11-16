import numpy as np
from FIPS import *
from DocType import *
import pandas as pd
from vars import *
from prettytable import PrettyTable
import csv
import os, csv
from Property import Property
from tqdm import tqdm
from collections import defaultdict
from csv import Sniffer
import glob
from vars import *
from math import isnan
from pathlib import Path

def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def capitalize_first(string):
    return string[0].upper() + string[1:].lower()

def load_fips_from_csv(): 
    df = pd.read_csv(FIPS_PATH, sep=';')
    fips_list = [Fips(row['FIPS Code'], capitalize_first(row['County Name']), row['Postal State'], row['Code']) for _, row in df.iterrows()]
    return fips_list

def consolidate_csvs():
    # Define the path to the folder
    folder_path = os.path.join("input", CLIENT_NAME)
    
    # Get a list of all the .csv files in that directory
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Check if there are any .csv files
    if not csv_files:
        print("No .csv files found in the specified directory.")
        return

    # Read the first .csv file
    consolidated_data = pd.read_csv(os.path.join(folder_path, csv_files[0]),low_memory=False)

    # Iterate through the rest of the .csv files and append to the consolidated dataframe
    for file in csv_files[1:]:
        current_data = pd.read_csv(os.path.join(folder_path, file), low_memory=False)
        consolidated_data = pd.concat([consolidated_data, current_data], ignore_index=True)

    # Output file name
    file_name = os.path.join("input", CLIENT_NAME, f"{CLIENT_NAME} - consolidated.csv")

    # Delete the file if it already exists
    if os.path.exists(file_name):
        os.remove(file_name)
    
    # Save the consolidated data into a single .csv file
    consolidated_data.to_csv(file_name, index=False)
    print("Files consolidated successfully!")
    return file_name

def process_csv_file(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # 1. Select specific columns from the dataframe
    selected_columns = [
        "FIPS", "PropertyID", "APN", "TaxAccountNumber", "SitusFullStreetAddress", "SitusCity", "SitusState", "SitusZIP5", 
        "LotSizeSqFt", "Owner1LastName", "Owner1FirstName", "Owner1MiddleName", "Owner2LastName", "Owner2FirstName", 
        "Owner2MiddleName", "OwnerNAME1FULL", "OwnerNAME2FULL", "MailingFullStreetAddress", "MailingUnitNbr", "MailingCity", 
        "MailingState", "MailingZIP5", "SumLivingAreaSqFt", "YearBuilt", "EffectiveYearBuilt", "CurrentSaleTransactionId", 
        "CurrentSaleRecordingDate", "CurrentSaleContractDate", "CurrentSaleDocumentType", "CurrentSalesPrice", 
        "CurrentSalesPriceCode", "CurrentSaleBuyer1FullName", "CurrentSaleBuyer2FullName", "CurrentSaleSeller1FullName", 
        "CurrentSaleSeller2FullName", "PrevSaleTransactionId", "PrevSaleRecordingDate", "PrevSaleContractDate", 
        "PrevSaleDocumentType", "PrevSalesPrice", "PrevSalesPriceCode", "PrevSaleBuyer1FullName", "PrevSaleBuyer2FullName", 
        "PrevSaleSeller1FullName", "PrevSaleSeller2FullName", "CurrentAVMValue", "vConfidenceScore", "RecordingDate_Deed", 
        "SaleDate_Deed", "DocumentType_Deed", "DocumentType_Processed_Deed", "SaleAmt_Deed", "saleDate_Processed_Deed", 
        "Owner_Type", "Use_Type", "saleDate", "totalValue", "buildDate", "LTV", "Absentee"
    ]
    df = df[selected_columns]

    # 2. Convert all columns to string type
    df = df.astype(str)

    # 3. Filter out rows where SitusFullStreetAddress and SitusZIP5 are blank
    df = df[(df["SitusFullStreetAddress"] != "") & (df["SitusZIP5"] != "")]

    # 4. Filter rows based on Use_Type containing either "SFH" or "Townhouse" or "2-9 units"
    df = df[df["Use_Type"].str.contains("SFH|Townhouse|2-9 units")]

    # Save the processed DataFrame back to the same CSV file
    df.to_csv(file_path, index=False)

    print("Processing complete. The CSV file has been updated.")

def load_properties_from_csv(file_path, RBB = False):
    fips_list, docType_list, zip_code_dict = load_data()
    if RBB == False:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            sniffer = Sniffer()
            dialect = sniffer.sniff(file.readline())
            file.seek(0)
        
        fips_to_county = {fips.fips_code: fips.county_name for fips in fips_list}
        fips_counter = defaultdict(int)

        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            total_rows = sum(1 for row in csv.reader(file, dialect=dialect)) - 1
            file.seek(0)

        properties_list = []
                
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, dialect=dialect)
            for row in tqdm(csv_reader, total=total_rows):
                # Filter out any None keys
                row = {k: v for k, v in row.items() if k is not None}

                current_fips = int(row.get('FIPS', 0))
    
                fips_counter[current_fips] += 1
                # Now row does not contain None as a key
                prop = Property(fips_list, docType_list, **row)
                properties_list.append(prop)

        return properties_list
    
    elif RBB:
        find_unmatched_properties(file_path, zip_code_dict)
        # Load the matching Excel data for comparison
        excel_file_path = f"input/{CLIENT_NAME}/client deals/{CLIENT_NAME} - client_deals.xlsx"
        excel_data = pd.read_excel(excel_file_path, dtype={'Property ZIP': str})
        excel_data['Property Address'] = excel_data['Property Address'].str.lower().str.strip()
        # Convert ZIP codes to strings, remove any '.0', and zero-fill to 5 digits
        excel_data['Property ZIP'] = excel_data['Property ZIP'].apply(
            lambda x: str(int(float(x))).zfill(5) if x not in [None, ''] else '')

        fips_to_county = {fips.fips_code: fips.county_name for fips in fips_list}
        fips_counter = defaultdict(int)

        with open(file_path, 'r', encoding='utf-8-sig') as file:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(file.readline())
            file.seek(0)
            total_rows = sum(1 for row in csv.reader(file, dialect=dialect)) - 1
            file.seek(0)

        properties_list = []
        
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, dialect=dialect)
            for row in tqdm(csv_reader, total=total_rows):
                # Filter out any None keys
                row = {k: v for k, v in row.items() if k is not None}

                current_fips = int(row.get('FIPS', 0))
                fips_counter[current_fips] += 1

                row_address = row.get('SitusFullStreetAddress', '').lower().strip()
                # Attempt to convert ZIP code to float, then to int, and format with leading zeros.
                # If conversion fails, default to '00000'.
                try:
                    row_zip = str(int(float(row.get('SitusZIP5', '0')))).zfill(5)
                except (ValueError, TypeError):
                    row_zip = '00000'

                # Instantiate Property for each row regardless of match
                prop = Property(fips_list, docType_list, **row)
                
                # Ensure excel_data 'Property ZIP' is also a zero-padded string for accurate comparison
                matched_row = excel_data[(excel_data['Property Address'] == row_address) & 
                                        (excel_data['Property ZIP'].str.zfill(5) == row_zip)]

                # If there's a match, then we update the prop accordingly
                if not matched_row.empty:
                    prop.case_1 = True
                    prop.case_2 = False
                    prop.case_3 = False
                    # Assuming 'Profit' is a column in the Excel file that corresponds to client_profit

                    prop.n_diffSalesPrice = matched_row['Profit'].iloc[0] if 'Profit' in matched_row.columns else 0
                
                else:
                    prop.case_1 = False
                    prop.case_2 = False
                    prop.case_3 = False
                
                # Add Property instance to list whether it's a match or not
                properties_list.append(prop)

        return properties_list

def load_docType_from_csv():
    df = pd.read_csv(DOCTYPE_PATH, sep=';')
    docType_list = [DocType(row['CODE'], capitalize_first(row['DESC']), row['Consider as sale?']) for _, row in df.iterrows()]
    return docType_list

def load_zipcode_data():
    # Read the data
    df = pd.read_excel(ZIPCODE_PATH)
    # Ensure zip code is a string to keep leading zeros
    df['zip code'] = df['zip code'].astype(str).str.zfill(5)
    # Create a dictionary for faster zip code lookup
    zip_code_dict = df.set_index('zip code')['county'].to_dict()
    return zip_code_dict

def load_data():
    fips_list       = load_fips_from_csv()
    docType_list    = load_docType_from_csv()
    zip_code_dict   = load_zipcode_data()
    return fips_list, docType_list, zip_code_dict

def find_county_by_zipcode(zip_code_dict, zip_code):
    # Normalize zip code input to string and fill leading zeros if needed
    # Handle cases where zip code could be a float, int, or str
    if isinstance(zip_code, float):
        # Check if it's an integer value in the float
        if zip_code.is_integer():
            zip_code = str(int(zip_code)).zfill(5)
        else:
            return "Invalid zip code format"
    elif isinstance(zip_code, int):
        zip_code = str(zip_code).zfill(5)
    elif isinstance(zip_code, str):
        # Clean and prepare the zip code string
        zip_code = zip_code.split('.')[0]  # Remove decimal part if any
        zip_code = zip_code.zfill(5)
    else:
        return "Invalid zip code format"

    # Find the county by zip code
    return zip_code_dict.get(zip_code, "Zip code not found")

def display_fips_info(fips_list, fips_codes):
    # Create a PrettyTable object
    table = PrettyTable()
    
    # Define the column headers
    table.field_names = ["FIPS Code", "County Name"]
    
    # Set table alignment
    table.align["FIPS Code"] = "l"
    table.align["County Name"] = "l"
    
    # Set border style
    table.border = True
    table.horizontal_char = "="
    table.vertical_char = "|"
    table.junction_char = "+"

    # Loop through the list of FIPS codes given as input
    for fips_code in fips_codes:
        # Find the corresponding FIPS object in the fips_list
        for fips_obj in fips_list:
            if fips_obj.fips_code == fips_code:
                # Add a row to the table with the FIPS code and county name
                table.add_row([fips_code, fips_obj.county_name])
                break
    
    return str(table)

def print_fips_summary(file_path, fips_instances):
    # Create a mapping of FIPS code to county name from the list of FIPS instances
    fips_to_county = {str(instance.fips_code): instance.county_name for instance in fips_instances}

    # Auto-detect the delimiter
    with open(file_path, 'r') as f:
        line = f.readline()
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(line).delimiter

    # Load the CSV file into a DataFrame with the detected delimiter
    df = pd.read_csv(file_path, delimiter=delimiter, low_memory=False)

    # Calculate the count and percentage for each FIPS
    fips_summary = df.groupby('FIPS').size().reset_index(name='# properties')
    total_properties = fips_summary['# properties'].sum()
    fips_summary['% Properties'] = (fips_summary['# properties'] / total_properties) * 100

    # Format the values
    fips_summary['FIPS'] = fips_summary['FIPS'].astype(int).astype(str)
    fips_summary['# properties'] = fips_summary['# properties'].apply(lambda x: f"{x:,}")  # thousand separator
    fips_summary['County'] = fips_summary['FIPS'].apply(lambda x: fips_to_county.get(x, "Unknown"))

    # Print the table header
    print("Row".ljust(5), "|", "FIPS".ljust(10), "|", "County".ljust(15), "|", "# properties".ljust(15), "|", "% Properties")
    print("-" * 65)

    # Print each row of the summary table
    for idx, row in fips_summary.iterrows():
        print(f"{(idx + 1):<5} | {row['FIPS'].ljust(10)} | {row['County'].ljust(15)} | {row['# properties'].ljust(15)} | {row['% Properties']:.2f}%")
    
    # Print the total properties
    print("-" * 65)
    print(f"Total Properties: {total_properties:,}")
    
def print_properties_in_table(properties):
    # Define the table and its columns
    table = PrettyTable()
    table.field_names = ["PropertyID", 
                         "PrevSaleBuyer1FullName", 
                         "CurrentSaleBuyer1FullName", 
                         "PrevSalesPrice", 
                         "MonthsSincePrevSale", 
                         "PrevSaleValid", 
                         "MonthsSinceCurrentSale", 
                         "CurrentSaleValid",
                         "YearsSinceBuilt",
                         "diffSalesPrice", 
                         "PrevSalesPriceValue (40%)",
                         "PrevDaysOwnership",
                         "CurrentSalesPriceValue", 
                         "Total Value (10%)",
                         "Case 1", 
                         "Case 2", 
                         "Case 3"]
    
    # Loop through each property and add a row to the table
    for prop in properties:
        row = [
            prop.PropertyID,
            prop.PrevSaleBuyer1FullName,
            prop.CurrentSaleBuyer1FullName,
            prop.PrevSalesPrice,
            prop.n_monthsSincePrevSale,
            prop.n_prevSaleValid,
            prop.n_monthsSinceCurrentSale,
            prop.n_currentSaleValid,
            prop.n_yearsSinceBuilt,
            prop.n_diffSalesPrice,         
            round(int(prop.n_prevSalesPriceValue) * 0.4,2),  
            prop.n_prevDaysOwnership,
            prop.n_currentSalesPriceValue,
            round(int(prop.totalValue) * 0.1,2),
            prop.case_1,
            prop.case_2,
            prop.case_3
        ]
        table.add_row(row)
    
    # Print the table
    print(table)

def is_non_disclosure_state(state_abbr):
    # List of abbreviations for non-disclosure states
    non_disclosure_states = ['AK', 'ID', 'KS', 'MO', 'MS', 'LA', 'WY', 'UT', 'TX', 'ND', 'NM', 'MT']
    return state_abbr.upper() in non_disclosure_states

def generate_and_display_case_report(properties):
    # Initialize counters for each case
    case_1_count = 0
    case_2_count = 0
    case_3_count = 0

    # Loop through each property instance and update the counters based on the cases
    for property_instance in properties:
        if property_instance.case_1:
            case_1_count += 1
        if property_instance.case_2:
            case_2_count += 1
        if property_instance.case_3:
            case_3_count += 1

    # Create a PrettyTable object
    table = PrettyTable()
    
    # Define the column headers
    table.field_names = ["Case", "Number of Properties"]
    
    # Populate the table with data
    table.add_row(['Case 1', case_1_count])
    table.add_row(['Case 2', case_2_count])
    table.add_row(['Case 3', case_3_count])
    table.add_row(['Total', case_1_count + case_2_count + case_3_count])
    
    return str(table)

def count_failed_criteria(property_instances):
    failed_criteria_counter = {
        'Base_criteria': 0,
        'Months_since_PrevSale': 0,
        'Months_since_CurrentSale': 0,
        'Years_since_built': 0,
        'Diff_in_Sales_Price': 0,
        'Previous_Days_of_Ownership': 0,
        'Current_Sales_Price': 0
    }
    
    for instance in property_instances:
        if not instance.Base_criteria():
            failed_criteria_counter['Base_criteria'] += 1
            
        months_since_prev_sale = to_int(instance.n_monthsSincePrevSale)
        if months_since_prev_sale is None or months_since_prev_sale > 12 or instance.n_prevSaleValid != "Y":
            failed_criteria_counter['Months_since_PrevSale'] += 1
            
        months_since_current_sale = to_int(instance.n_monthsSinceCurrentSale)
        if months_since_current_sale is None or months_since_current_sale > 12 or instance.n_currentSaleValid != "Y":
            failed_criteria_counter['Months_since_CurrentSale'] += 1
        
        years_since_built = to_float(instance.n_yearsSinceBuilt)
        if years_since_built is None or years_since_built <= 3:
            failed_criteria_counter['Years_since_built'] += 1
        
        diff_in_sales_price = to_float(instance.n_diffSalesPrice)
        if diff_in_sales_price is None or diff_in_sales_price <= 10000 or diff_in_sales_price > instance.n_currentSalesPriceValue * 0.4:
            failed_criteria_counter['Diff_in_Sales_Price'] += 1
        
        prev_days_ownership = to_int(instance.n_prevDaysOwnership)
        if prev_days_ownership is None or not (0 <= prev_days_ownership <= 3):
            failed_criteria_counter['Previous_Days_of_Ownership'] += 1
        
        current_sales_price = to_float(instance.n_currentSalesPriceValue)
        total_value = to_float(instance.totalValue)
        if current_sales_price is None or total_value is None or current_sales_price <= 0.10 * total_value or current_sales_price <= 20000:
            failed_criteria_counter['Current_Sales_Price'] += 1
    
    total_instances = len(property_instances)
    
    # Create a PrettyTable object
    x = PrettyTable()
    
    # Define the column names
    x.field_names = ["Criteria", "Count", "% Failed"]
    
    # Loop through each criteria to add rows to the table
    for criteria, count in failed_criteria_counter.items():
        percentage_failed = (count / total_instances) * 100
        x.add_row([criteria, count, f"{percentage_failed:.2f}%"])
        
    # Display the table
    print(x)
    
def export_cases(properties_list, RBB = False):
    if RBB:
        file_cases = "output/RBB_cases - " + CLIENT_NAME  # Notice the .xlsx is removed
    else:
        file_cases = "output/MRBB_cases - " + CLIENT_NAME  # Notice the .xlsx is removed
    # Extract attributes into a list of dictionaries
    data = [prop.__dict__ for prop in properties_list]
    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Remove unwanted columns
    df.drop(['fips_list', 'docType_list'], axis=1, inplace=True)
    # Add 'Deal' column
    df['Deal'] = df.apply(lambda row: 1 if row['case_1'] or row['case_2'] or row['case_3'] else 0, axis=1)
    
    # Save to Excel
    # df.to_excel(file_cases, index=False)
    
    # Save to CSV in chunks
    chunk_size = 1000000
    for i in range(0, len(df), chunk_size):
        df.iloc[i:i+chunk_size].to_csv(f"{file_cases}_{i//chunk_size}.csv", index=False)
    
    # Count of exported rows (excluding header)
    exported_properties = len(properties_list)
    exported_deals = len(df[df['Deal'] == 1])
    print("Exported deals: {} from {} properties".format(exported_deals, exported_properties))

def read_cases(RBB):
    if RBB == False:
        file_prefix = "output/MRBB_cases - " + CLIENT_NAME + "_"
    if RBB == True:
        file_prefix = "output/RBB_cases - " + CLIENT_NAME + "_"
    all_files = glob.glob(f"{file_prefix}*.csv")
    df_from_each_file = (pd.read_csv(f, low_memory=False) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df

def create_cases_table(file_path, RBB = False):
    # Commented list
    all_columns = ["buildDate", "case_1", "case_2", "case_3",
        "FIPS", "LotSizeSqFt", "LTV",
        "MailingCity", "MailingFullStreetAddress", "MailingState",
        "MailingZIP5", "n_county", "n_currentSaleSellerROI",
        "n_diffSalesPrice", "n_discounted", "n_dSPtV", "n_livingAreaSqFt",
        "n_lotSizeSqFt", "n_monthsSincePrevSale", "n_prevDaysOwnership",
        "n_totalValue", "n_yearsSinceBuilt", "Owner_Type", "OwnerNAME1FULL",
        "PropertyID", "saleDate", "SitusCity", "SitusFullStreetAddress",
        "SitusState", "SitusZIP5", "SumLivingAreaSqFt", "totalValue", "Use_Type", 'Deal']

    # Official list
    official_columns = [
        'APN',
        'SitusFullStreetAddress',
        'SitusZIP5',
        'n_diffSalesPrice',
        'n_lotSizeSqFt',
        'buildDate',
        'Use_Type',
        'saleDate',
        'n_livingAreaSqFt',
        'n_totalValue',
        'n_county',
        'case_1',
        'case_2',
        'case_3',
        'Deal'
    ]

    # Find missing variables
    missing_columns = [col for col in all_columns if col not in official_columns]

    # # Add missing variables to the end of the official list
    official_columns.extend(missing_columns)
    
    # Read the Excel file into a DataFrame
    df = read_cases(RBB)
    
    # Filter the DataFrame to only include specified columns
    df_filtered = df[official_columns].copy()  # Make a copy to avoid SettingWithCopyWarning
    
    # Handle 'Unknown' in LTV  
    df_filtered['case_1'] = df_filtered['case_1'].astype(int)
    df_filtered['case_2'] = df_filtered['case_2'].astype(int)
    df_filtered['case_3'] = df_filtered['case_3'].astype(int)

    df_filtered['Deal'] = df_filtered['case_1'] | df_filtered['case_2'] | df_filtered['case_3']
    
    # Filter rows where Deal == 1
    df_filtered = df_filtered[df_filtered['Deal'] == 1]
    
    # Assuming you have a DataFrame named df
    df_filtered.rename(columns={"SitusZIP5": "ZipCode"}, inplace=True)
    
    # Filter out rows with non-finite values in 'ZipCode' column
    df_filtered = df_filtered[df_filtered['ZipCode'].notna() & ~df_filtered['ZipCode'].isin([np.inf, -np.inf])]

    # Convert ZipCode to string, handle NaN or inf, and transform '.0' to float
    df_filtered['ZipCode'] = df_filtered['ZipCode'].fillna(0).astype(float)

    # Filter out rows with NaN values in 'ZipCode' column
    df_filtered = df_filtered[df_filtered['ZipCode'].notna()]

    # Convert ZipCode to integer and then to string
    df_filtered['ZipCode'] = df_filtered['ZipCode'].astype(int).astype(str).str.zfill(5)
    
    # Columns to be deleted before exporting
    cols_to_delete = [
        'Deal', 'FIPS', 'LotSizeSqFt', 'LTV', 'MailingCity', 
        'MailingFullStreetAddress', 'MailingState', 'MailingZIP5',
        'n_currentSaleSellerROI', 'n_discounted', 'n_dSPtV', 'n_monthsSincePrevSale',
        'n_prevDaysOwnership', 'n_yearsSinceBuilt', 'Owner_Type', 'OwnerNAME1FULL',
        'PropertyID', 'SitusCity', 'SitusState', 'SumLivingAreaSqFt', 'totalValue'
    ]
    
    # Drop the columns
    df_filtered.drop(columns=cols_to_delete, inplace=True)
    
    # Drop duplicates by 'APN' to avoid exporting duplicate properties
    df_filtered.drop_duplicates(subset='APN', keep='first', inplace=True)

    # Save the filtered DataFrame as a new Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='Market')

def evaluate_priority(num_deals, cumulative_revenue_percent, avg_revenue, avg_revenue_per_deal):
    more_than_two_deals = num_deals > 2
    less_than_two_deals = num_deals <= 2
    
    within_first_80_percent = cumulative_revenue_percent <= 0.8
    within_80_to_90_percent = 0.8 < cumulative_revenue_percent <= 0.9
    within_90_to_100_percent = 0.9 < cumulative_revenue_percent < 1

    lower_avg_revenue = avg_revenue < 0.5 * avg_revenue_per_deal
    mid_avg_revenue = 0.5 * avg_revenue_per_deal <= avg_revenue < 0.75 * avg_revenue_per_deal
    high_avg_revenue = avg_revenue >= 0.75 * avg_revenue_per_deal
    
    if more_than_two_deals and within_first_80_percent and mid_avg_revenue:
        return 2
    if more_than_two_deals and within_first_80_percent and lower_avg_revenue:
        return 3
    if more_than_two_deals and within_first_80_percent and high_avg_revenue:
        return 1
    
    if more_than_two_deals and within_80_to_90_percent and mid_avg_revenue:
        return 3
    if more_than_two_deals and within_80_to_90_percent and lower_avg_revenue:
        return 4
    if less_than_two_deals and within_80_to_90_percent and high_avg_revenue:
        return 2
    
    if more_than_two_deals and within_90_to_100_percent and mid_avg_revenue:
        return 4
    if more_than_two_deals and within_90_to_100_percent and lower_avg_revenue:
        return 5
    if less_than_two_deals and within_90_to_100_percent and high_avg_revenue:
        return 3
    else:
        return 5

def set_MRBB(properties_list, file_path):
    table_data = defaultdict(lambda: defaultdict(int))

    total_revenue = 0

    for prop in tqdm(properties_list, desc='Processing Properties'):
        zipcode = prop.SitusZIP5
        if zipcode == "nan":
            continue

        zipcode = int(float(zipcode))
        county = prop.n_County()
        use_type = prop.Use_Type
        diff_sales_price = prop.n_DiffSalesPrice()
        is_valid_deal = prop.case_1 or prop.case_2 or prop.case_3

        if use_type == "SFH":
            table_data[zipcode]['SFH Counts'] += 1

        table_data[zipcode]['County'] = county

        if prop.case_1:
            table_data[zipcode]['Double Close'] += 1
        if prop.case_2:
            table_data[zipcode]['Wholetail'] += 1
        if prop.case_3:
            table_data[zipcode]['Fix & Flip'] += 1

        if is_valid_deal:
            table_data[zipcode]['# Deals'] += 1
            table_data[zipcode]['Revenue'] += diff_sales_price
            total_revenue += diff_sales_price

    # Filter ZIP codes without valid deals
    table_data = {k: v for k, v in table_data.items() if v['# Deals'] > 0}

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(table_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'ZIP CODE'}, inplace=True)

    # Calculate additional columns
    df['% Revenue'] = (df['Revenue'] / total_revenue)
    df['AVG Revenue'] = df['Revenue'] / df['# Deals'] 
    
    df = df.sort_values('Revenue', ascending=False)
    df['Cumulative Revenue %'] = df['% Revenue'].cumsum()
    
    # Existing columns in df
    existing_columns = df.columns.tolist()

    # Desired columns order
    desired_columns = ['ZIP CODE', 'SFH Counts', 'County', 'Double Close', 'Wholetail', 'Fix & Flip', '# Deals', 'Revenue', '% Revenue', 'AVG Revenue', 'Cumulative Revenue %']

    # Columns that are missing from df but are in desired_columns
    missing_columns = [col for col in desired_columns if col not in existing_columns]

    # Add missing columns to df with default value of 0
    for col in missing_columns:
        df[col] = 0

    # Now reorder df
    df = df[desired_columns]


    # Reorder columns
    df = df[['ZIP CODE', 'SFH Counts', 'County', 'Double Close', 'Wholetail', 'Fix & Flip', '# Deals', 'Revenue', '% Revenue', 'AVG Revenue', 'Cumulative Revenue %']]
    
    # Calculate the average revenue per deal for the entire dataset
    total_deals = sum(v['# Deals'] for v in table_data.values())
    avg_revenue_per_deal = total_revenue / total_deals

    # Apply the evaluate_priority function row-wise
    df['Priority'] = df.apply(
        lambda row: evaluate_priority(
            row['# Deals'], row['Cumulative Revenue %'], row['AVG Revenue'], avg_revenue_per_deal
        ),
        axis=1
    )
    
    ensure_file_exists(CLIENT_NAME)
        
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='MRBB', index=False)
 
def create_zipcode_table(properties_list, file_path):
    # Extract ZipCodes and Counties from properties_list
    zipcodes = [prop.SitusZIP5 for prop in properties_list]
    counties = [prop.n_county for prop in properties_list]
    
    # Zip them together and then create a DataFrame
    zipped_data = list(zip(zipcodes, counties))
    df = pd.DataFrame(zipped_data, columns=['ZipCode', 'County'])
    
    # Count occurrences of each ZipCode
    df_count = df['ZipCode'].value_counts().reset_index()
    df_count.columns = ['ZipCode', 'Count']
    
    # Remove duplicates and keep County information
    df = df.drop_duplicates(subset='ZipCode')
    
    # Merge both DataFrames on ZipCode
    df = pd.merge(df_count, df, on='ZipCode')
    
    # Filter out rows with non-finite values in 'ZipCode' column
    df = df[df['ZipCode'].notna() & ~df['ZipCode'].isin([np.inf, -np.inf])]

    # Convert ZipCode to string, handle NaN or inf, and transform '.0' to float
    df['ZipCode'] = df['ZipCode'].fillna(0).astype(float)

    # Filter out rows with NaN values in 'ZipCode' column
    df = df[df['ZipCode'].notna()]

    # Convert ZipCode to integer and then to string
    df['ZipCode'] = df['ZipCode'].astype(int).astype(str).str.zfill(5)
    
    # Replace '00nan' with 'Unknown'
    df['ZipCode'] = df['ZipCode'].replace('00nan', 'Unknown')
    
    # Sort by ZipCode for better readability
    df.sort_values(by="ZipCode", inplace=True)
    
    # Save the DataFrame to Excel in 'ZipCode' sheet
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='ZipCode', index=False)
    
    return df

def create_year_county_table(properties_list, file_path):
    # Define the ranges
    ranges = [("Unknown", None, None),
                ("0", 0, 2),
                ("2", 2, 5),
                ("5", 5, 8),
                ("8", 8, 10),
                ("10", 10, 15),
                ("15", 15, 20),
                ("20", 20, 25),
                ("25", 25, 30),
                ("30", 30, 40),
                ("40", 40, 50),
                ("50", 50, 75),
                ("75", 75, 100),
                ("100", 100, float('inf'))]

    table_data = {name: {} for name, _, _ in ranges}

    # Populate the table data
    for prop in properties_list:
        year_built = prop.n_yearsSinceBuilt
        county = prop.n_county

        # Categorize the year_built into the right range
        for name, start, end in ranges:
            if year_built == "" or year_built is None:
                category = "Unknown"
                break
            elif start is not None and end is not None and start <= float(year_built) < end:
                category = name
                break
            else:
                continue

        table_data[category][county] = table_data[category].get(county, 0) + 1

    df = pd.DataFrame.from_dict(table_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Year Built'}, inplace=True)
    
    cols = list(df.columns)
    cols.remove('Year Built')
    cols.sort()
    df = df[['Year Built'] + cols]

    
    # Filter out the row with 'Unknown' in 'Year Built'
    unknown_row = df[df['Year Built'] == 'Unknown']
    df = df[df['Year Built'] != 'Unknown']

    # Convert all columns to numeric, coerce errors
    for col in df.columns:
        if col != 'Year Built':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Append the 'Unknown' row back
    df = pd.concat([unknown_row, df], ignore_index=True)
    
    # Save the DataFrame to an Excel file
    
    # Save the DataFrame to Excel in 'ZipCode' sheet
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Year Built', index=False)
        
    return df

def create_total_value_table(properties_list, file_path):
    value_ranges = [0, 1, 25000, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 
                    400000, 500000, 600000, 750000, 1000000, 1500000, 2000000, float('inf')]
    
    # Ensure 'Total Value' has one entry for each range plus one for "Unknown"
    data = {"Total Value": ["Unknown", "$0", "$1", "$25,000", "$50,000", "$100,000", "$150,000", "$200,000", 
                            "$250,000", "$300,000", "$350,000", "$400,000", "$500,000", "$600,000", 
                            "$750,000", "$1,000,000", "$1,500,000", "$2,000,000"]}
    
    unique_counties = set(prop.n_county for prop in properties_list)
    
    for county in unique_counties:
        counts = []
        county_properties = [prop for prop in properties_list if prop.n_county == county]
        
        # Calculate "Unknown" count - This is fine
        unknown_count = sum(np.isnan(prop.n_totalValue) or prop.n_totalValue == '' for prop in county_properties)
        counts.append(unknown_count)
        
        # Check each range and append the count - This should be fine as long as 'n_totalValue' is numeric
        for i in range(len(value_ranges) - 1):
            count = sum(value_ranges[i] <= prop.n_totalValue < value_ranges[i+1] for prop in county_properties)
            counts.append(count)

        # The error is likely due to an incorrect count list length
        # Ensure that 'counts' has the same number of elements as 'Total Value'
        if len(counts) != len(data["Total Value"]):
            raise ValueError(f"Counts for {county} do not match 'Total Value' length: {len(counts)} != {len(data['Total Value'])}")
        
        data[county] = counts
    
    try:
        df = pd.DataFrame(data)
    except ValueError as e:
        # Add more informative error logging here if necessary
        print("Error in creating DataFrame: ", e)
        raise

    cols = list(df.columns)
    cols.remove('Total Value')
    cols.sort()
    df = df[['Total Value'] + cols]
    
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Total Value', index=False)
        
    return df

def create_living_area_table(properties_list, file_path):
    # Define the living area ranges in SqFt
    area_ranges = [0, 1, 200, 800, 1500, 2000, 2500, 3000, 3500, 4500, float('inf')]
    
    # Initialize a dictionary to store data
    data = {
        "Living Area SqFt": ["Unknown", "0", "1", "200", "800", "1500", "2000", "2500", "3000", "3500", "4500"]
    }

    # Extract unique counties from properties_list
    unique_counties = set(prop.n_county for prop in properties_list)

    # Loop through each unique county and calculate counts for each area range
    for county in unique_counties:
        counts = []
        # First, handle 'Unknown' cases
        unknown_count = sum(prop.n_livingAreaSqFt in [None, "", "NaN"] for prop in properties_list if prop.n_county == county)
        counts.append(unknown_count)

        county_properties = [prop for prop in properties_list if prop.n_county == county]
        for i in range(len(area_ranges) - 1):
            count = sum(area_ranges[i] <= float(prop.n_livingAreaSqFt) < area_ranges[i+1] for prop in county_properties)
            counts.append(count)
        data[county] = counts

    # Create a DataFrame
    df = pd.DataFrame(data)

    cols = list(df.columns)
    cols.remove('Living Area SqFt')
    cols.sort()
    df = df[['Living Area SqFt'] + cols]

    # Save the DataFrame to Excel in 'Living Area' sheet
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Living Area', index=False)
        
    return df

def create_lot_size_table(properties_list, file_path):
    # Define the lot size ranges
    lot_size_ranges = [0, 1, 101, 1000, 3600, 15000, 30000, 45000, float('inf')]
    
    # Initialize a dictionary to store data, add "Unknown" at the start
    data = {"Lot Size SqFt": ["Unknown", "0", "1", "101", "1000", "3600", "15000", "30000", "45000"]}
    
    # Extract unique counties from properties_list
    unique_counties = set(prop.n_county for prop in properties_list)

    # Loop through each unique county and calculate counts for each lot size range
    for county in unique_counties:
        counts = [0]  # Initialize "Unknown" count to 0
        county_properties = [prop for prop in properties_list if prop.n_county == county]
        
        # Count "Unknown" Lot Size SqFt
        counts[0] = sum(isnan(float(prop.n_lotSizeSqFt)) or prop.n_lotSizeSqFt == "" for prop in county_properties)
        
        for i in range(len(lot_size_ranges) - 1):
            count = sum(lot_size_ranges[i] <= float(prop.n_lotSizeSqFt) < lot_size_ranges[i+1] for prop in county_properties)
            counts.append(count)
        data[county] = counts

    # Create a DataFrame
    df = pd.DataFrame(data)
    
    cols = list(df.columns)
    cols.remove('Lot Size SqFt')
    cols.sort()
    df = df[['Lot Size SqFt'] + cols]

    # Save the DataFrame to Excel in 'Lot Size' sheet
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Lot Size', index=False)
        
    return df

def create_deal_summary(file_path, RBB = False):
    # Load the excel file
    df = read_cases(RBB)
    
    # Filtering helper function
    def filter_avg_values(series):
        q10, q90 = series.quantile([0.1, 0.9])
        return series[(series != 0) & (series != "unknown") & (series > q10) & (series < q90)].mean()
    
    # Group by n_county and perform necessary aggregations for all properties
    grouped_props = df.groupby('n_county').agg(
        Num_Properties=pd.NamedAgg(column='Use_Type', aggfunc='size'),
        Avg_Value=pd.NamedAgg(column='n_totalValue', aggfunc=filter_avg_values),
        Avg_Lot_Size=pd.NamedAgg(column='n_lotSizeSqFt', aggfunc=filter_avg_values),
        Avg_Liv_Area=pd.NamedAgg(column='n_livingAreaSqFt', aggfunc=filter_avg_values)
    ).reset_index()
    
    # Group by n_county and perform necessary aggregations for deals
    df_deal = df[df['Deal'] == 1]
    grouped_deal = df_deal.groupby('n_county').agg(
        Deals=pd.NamedAgg(column='Deal', aggfunc=lambda x: (x == 1).sum()),
        Total_Deal_Revenue=pd.NamedAgg(column='n_diffSalesPrice', aggfunc='sum')  # Changed here to sum
    ).reset_index()

    # ... [rest of the function code remains unchanged]

    # Use Total_Deal_Revenue directly instead of calculating Revenue
    grouped = pd.merge(grouped_props, grouped_deal, on='n_county', how='left')

    # ... [rest of the function code remains unchanged]

    # Renaming the column headers to reflect the new calculation
    grouped = grouped.rename(columns={
        "n_county": "County",
        "Deals": "# Deals",
        "Total_Deal_Revenue": "Revenue"  # Changed here to reflect the correct terminology
    })
    
    # Reordering columns
    reordered_cols = ['County', 'Num_Properties', 'Avg_Value', 'Avg_Lot_Size', 'Avg_Liv_Area', '# Deals', 'Revenue']
    grouped = grouped.loc[:, reordered_cols]
    
    # Save the grouped DataFrame to a new Excel sheet
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        grouped.to_excel(writer, sheet_name='Counties', index=False)

    return grouped

def delete_tables_file(file_path):   
    if os.path.exists(file_path):
        os.remove(file_path)
        # print(f"'{file_name}' has been deleted.")
    else:
        pass
        # print(f"'{file_name}' does not exist.")

def ensure_file_exists(file_path):    
    if not os.path.exists(file_path):
        # Create an empty DataFrame and save it to initiate the file
        df_empty = pd.DataFrame()
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_empty.to_excel(writer, sheet_name='Init', index=False)
        print(f"'{file_path}' has been created.")  

def delete_csv_files(directory='output'):
    # Get list of all .csv files in the specified directory
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    
    # Loop through the list and delete each file
    for file_path in csv_files:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}') 
    # Output file name
    file_name = os.path.join("input", CLIENT_NAME, f"{CLIENT_NAME} - consolidated.csv")

    # Check if the file exists before deleting it
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        pass
        # print(f"The file '{file_name}' does not exist.")
          
def create_tables(properties_list, RBB = False):
    if RBB == True:
        file_path   = "output/RBB_results - "  + CLIENT_NAME + ".xlsx"
    if RBB == False:
        file_path   = "output/MRBB_results - "  + CLIENT_NAME + ".xlsx"
    create_deal_summary(file_path, RBB)    
    create_zipcode_table(properties_list, file_path)   
    create_year_county_table(properties_list, file_path)   
    create_total_value_table(properties_list, file_path)   
    create_living_area_table(properties_list, file_path)    
    create_lot_size_table(properties_list, file_path)    
    create_cases_table(file_path, RBB)    
    delete_csv_files()

def find_unmatched_properties(large_file_path, zip_code_dict):
    small_file_path = f"input/{CLIENT_NAME}/client deals/{CLIENT_NAME} - client_deals.xlsx"
    
    # Load the datasets
    large_df = pd.read_csv(large_file_path)
    small_df = pd.read_excel(small_file_path)

    # Preprocessing to ensure the addresses and ZIPs are in the correct format for comparison
    large_df['SitusFullStreetAddress'] = large_df['SitusFullStreetAddress'].str.lower().str.strip()
    # Convert ZIP codes to integers, handling non-numeric and NaN values
    large_df['SitusZIP5'] = pd.to_numeric(large_df['SitusZIP5'], errors='coerce').fillna(0).astype(int)
    
    small_df['Property Address'] = small_df['Property Address'].str.lower().str.strip()
    small_df['Property ZIP'] = pd.to_numeric(small_df['Property ZIP'], errors='coerce').fillna(0).astype(int)

    # Merge the two dataframes on the specified conditions
    merged_df = small_df.merge(large_df, 
                               left_on=['Property Address', 'Property ZIP'], 
                               right_on=['SitusFullStreetAddress', 'SitusZIP5'], 
                               how='left', 
                               indicator=True)
    
    # After the merge operation
    matched_deals = merged_df[merged_df['_merge'] != 'left_only']
    total_deals = len(small_df)
    matched_count = len(matched_deals)
    matched_percentage = (matched_count / total_deals) * 100

    # Print statements
    print(f"Matched deals: {matched_count}")
    print(f"Matched Percentage: {matched_percentage:.2f}%")

    # Filter rows that didn't find a match in the large dataframe
    unmatched_df = merged_df[merged_df['_merge'] == 'left_only']

    # Add a new column 'County' based on 'Property ZIP'
    unmatched_df['County'] = unmatched_df['Property ZIP'].apply(lambda x: find_county_by_zipcode(zip_code_dict, x))

    # Return only the columns from the small file plus the new 'County' column and save to an Excel file
    columns_to_output = ['Property Address', 'Property ZIP', 'Profit', 'County']
    unmatched_properties = unmatched_df[columns_to_output]
    unmatched_properties.to_excel(f"output/unmatched client_deals - {CLIENT_NAME}.xlsx", index=False)