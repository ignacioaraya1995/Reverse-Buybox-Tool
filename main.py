from utils import *

RBB = True # If you want to make a MRBB, then RBB should be set to False, else RBB should be set to True.

if __name__ == "__main__":

    delete_csv_files()
    file_input = consolidate_csvs()
    process_csv_file(file_input)
    properties_list = load_properties_from_csv(file_input, RBB)    
    count_failed_criteria(properties_list)
    export_cases(properties_list, RBB)
    create_tables(properties_list, RBB)
    
    # RBB = True
    # delete_csv_files()
    # file_input = consolidate_csvs()
    # process_csv_file(file_input)
    # properties_list = load_properties_from_csv(file_input, RBB)    
    # export_cases(properties_list, RBB)
    # create_tables(properties_list, RBB)