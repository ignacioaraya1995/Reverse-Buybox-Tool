from utils import *
from vars import *

RBB = False # If you want to make a MRBB, then RBB should be set to False, else RBB should be set to True.

if __name__ == "__main__":
    print("Starting: ", CLIENT_NAME)
    delete_csv_files(CLIENT_NAME)
    file_input = consolidate_csvs(CLIENT_NAME)
    process_csv_file(CLIENT_NAME, file_input)
    properties_list = load_properties_from_csv(CLIENT_NAME, file_input, RBB)    
    # count_failed_criteria(properties_list)
    export_cases(CLIENT_NAME, properties_list, RBB)
    create_tables(CLIENT_NAME, properties_list, RBB)
    
    RBB = True
    delete_csv_files(CLIENT_NAME)
    file_input = consolidate_csvs(CLIENT_NAME)
    process_csv_file(CLIENT_NAME, file_input)
    properties_list = load_properties_from_csv(CLIENT_NAME, file_input, RBB)    
    export_cases(CLIENT_NAME, properties_list, RBB)
    create_tables(CLIENT_NAME, properties_list, RBB)
 

# if __name__ == "__main__2":
#     print("Starting: ", CLIENT_NAME)
#     delete_csv_files(CLIENT_NAME)
#     file_input = consolidate_csvs(CLIENT_NAME)
#     process_csv_file(CLIENT_NAME, file_input, False)
#     properties_list = load_properties_from_csv(CLIENT_NAME, file_input, False)      
#     print("Starting: ", CLIENT_NAME)    
#     property_management(properties_list, CLIENT_NAME)