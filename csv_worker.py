#!/usr/bin/env python

import csv
import os

NEW_COLS = ['Job', 'AA', 'Pass', 'List']
BLACKLIST = 'BLACKLIST.csv'

def get_csv_files(input_dir, suffix=".csv"):
    """
    Scan the input directory and return a list containing all the .csv files
    found there.

    :input: a directory containing input files
            suffix of the input files (by default set to ".csv")
    :return: list containing the csv files in input_dir (full path)
    """
    
    filenames = os.listdir(input_dir)
    return [os.path.join(input_dir, filename) for filename in filenames
            if filename.endswith(suffix)]

def not_empty(line):
    """
    Return false if line (a list) is filled with spaces or 'nothings'
    """
    for word in line:
        if word: return True
    return False

def not_on_blacklist(name, black_list):
    if name not in black_list:
        for bad_name in black_list:
            if bad_name in name:
                return False
    return True

def work_csv(infile):
    # add cols
    infile_name, infile_extn = os.path.splitext(infile)
    outfile = infile_name+'_COLLS_ADDED.csv'
    new_col_vals = infile_name.split('_')
    new_col_vals[2] = new_col_vals[2].split()[1] # remove 'Pass '
    with open(infile) as read_handler:
        with open(outfile, 'w') as write_handler:
            reader = csv.reader(read_handler)
            writer = csv.writer(write_handler)
            headers = reader.next()
            headers = NEW_COLS + headers
            writer.writerow(headers)
            for line in reader: 
                if not_empty(line):
                    writer.writerow(new_col_vals+line)
    added_cols = os.path.abspath(outfile)

    # remove duplicates
    no_dupls = added_cols
    no_dupls_name, no_dupls_ext = os.path.splitext(no_dupls)

    # filter blacklist
    no_dupls_blacklist = no_dupls_name + '_BLACKLIST' + no_dupls_ext
    with open(BLACKLIST) as black_handle:
        black_list = [line.strip() for line in black_handle 
                      if 'Blacklist' not in line]
        print black_list
        with open(no_dupls) as ndh:
            with open(no_dupls_blacklist, 'w') as ndbh:
                reader = csv.reader(ndh)
                writer = csv.writer(ndbh)
                for line in reader:
                    name = line[4]
                    if not_on_blacklist(name, black_list):
                        writer.writerow(line)
                    
    return (added_cols, no_dupls, no_dupls_blacklist)

if __name__ == "__main__":

    infile = '13_MD_Pass 1_RedHerring.csv'
    print(work_csv(infile))
