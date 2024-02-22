from utils import *
from vars import *

if __name__ == "__main__":
    # Ask the user for the client name
    client_name = input("Please enter the client name (it should match the client folder name): ")
    CLIENT_NAME = client_name.strip()  # .strip() removes any leading/trailing whitespace

    # Ask the user if they want to run only the Market Reverse Buybox (MRBB) or both MRBB and Reverse Buybox (RBB)
    process_choice = input("Do you want to run only the Market Reverse Buybox (MRBB) or both MRBB and Reverse Buybox (RBB)? Enter 'MRBB' for only MRBB or 'Both' for both: ").strip().lower()

    # Initialize to run MRBB first
    RBB = False
    print(f"Starting the Market Reverse Buybox (MRBB) for {CLIENT_NAME}")

    # Common process steps
    def process_steps(CLIENT_NAME, RBB):
        delete_csv_files(CLIENT_NAME)
        file_input = consolidate_csvs(CLIENT_NAME)
        process_csv_file(CLIENT_NAME, file_input)
        properties_list = load_properties_from_csv(CLIENT_NAME, file_input, RBB)    
        export_cases(CLIENT_NAME, properties_list, RBB)
        create_tables(CLIENT_NAME, properties_list, RBB)

    # Run the MRBB
    process_steps(CLIENT_NAME, RBB)

    # Check if the user wants to run both
    if process_choice == 'both':
        # Now run RBB
        RBB = True
        print(f"Starting the Reverse Buybox (RBB) for {CLIENT_NAME}")
        process_steps(CLIENT_NAME, RBB)
