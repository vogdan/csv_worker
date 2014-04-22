#!/usr/bin/env python

import csv
import os

NEW_COLS = ['Job', 'AA', 'Pass', 'List']
BLACKLIST = 'BLACKLIST.csv'

def get_csv_files(input_dir, suffix=".csv"):
    """
    Scan the input directory and return a list containing all the .csv files
    found there.

    :rtype: list
    :return: list containing the csv files in input_dir (full path)
    """
    
    filenames = os.listdir(input_dir)
    return [os.path.join(input_dir, filename) for filename in filenames
            if filename.endswith(suffix)]

def not_empty(line):
    """
    Check if line is filled with whitespaces
    
    :rtype: Boolean
    :return: True - line not empty
             False - line is empty
    """
    for word in line:
        if word: return True
    return False

def not_on_blacklist(name, black_list):
    """
    Check if the name is on the blacklist

    :type name: str
    :param name: string to check

    :type black_list: list of str
    :param black_list: list of strings to check against

    :rtype: Boolean
    :return: True - if name not in black_list 
                     or blacklist entry not contained in name
             False - otherwise        
    """
    if name not in black_list:
        for bad_name in black_list:
            if bad_name in name:
                return False
    return True

def add_cols(input_file, output_file):
    """
    Parse file name and add four columns to the file with the parsed info
    
    :rtype: str
    :return: absolute path to modified file
    """
    new_col_vals = input_file_name.split('_')
    new_col_vals[2] = new_col_vals[2].split()[1] # remove 'Pass '
    with open(input_file) as read_handler:
        with open(output_file, 'w') as write_handler:
            reader = csv.reader(read_handler)
            writer = csv.writer(write_handler)
            headers = reader.next()
            headers = NEW_COLS + headers
            writer.writerow(headers)
            for line in reader: 
                if not_empty(line):
                    writer.writerow(new_col_vals+line)
    return os.path.abspath(out_file)


def merge_files(input_dir, output_file):
    """
    Scan input dir and merge all csv files found into a master spreadsheet


    :type input_dir: str
    :param input_dir: Path to input directory (path must exist)

    :type output_file: str
    :param output_file: Absolute path and name of output file

    :rtype: str
    :return: absolute path to master spreadsheet
    """
    pass

def remove_duplicate_lines(input_file, output_file):
    pass

def filter_blacklist(input_file, output_file, blacklist_header='Blacklist'):
    with open(BLACKLIST) as black_handle:
        black_list = [line.strip() for line in black_handle 
                      if blacklist_header not in line]
        with open(input_file) as in_handle:
            with open(output_file, 'w') as out_handle:
                reader = csv.reader(in_handle)
                writer = csv.writer(out_handle)
                for line in reader:
                    name = line[4]
                    if not_on_blacklist(name, black_list):
                        writer.writerow(line)
    return os.path.abspath(blacklist_filtered)

if __name__ == "__main__":
    input_file_name, input_file_extn = os.path.splitext(input_file)
    output_file = input_file_name+'_COLLS_ADDED.csv'
    
