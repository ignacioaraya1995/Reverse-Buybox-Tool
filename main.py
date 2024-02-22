from utils import *
from vars import *

if __name__ == "__main__":
    client_folders = list_client_folders()
    if client_folders:
        CLIENT_NAME = get_client_selection(client_folders)
        print(f"Selected client: {CLIENT_NAME}")
        # Ask the user if they want to run only the Market Reverse Buybox (MRBB) or both MRBB and Reverse Buybox (RBB)
        process_choice = input("Run 'MRBB' only or both 'MRBB' and 'RBB'? Enter 'MRBB' or 'Both':").strip().lower()

        # Initialize to run MRBB first
        RBB = False
        print(f"\nStarting the Market Reverse Buybox (MRBB) for {CLIENT_NAME}")

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
            print(f"\nStarting the Reverse Buybox (RBB) for {CLIENT_NAME}")
            try:
                process_steps(CLIENT_NAME, RBB)
            except:
                print("Error with the RBB, please check the file name, or maybe it does not exist (and check the columns)")
