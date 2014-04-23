#!/usr/bin/env python

import csv
import os
import sys
import traceback

NEW_COLS = ['Job', 'AA', 'Pass', 'List']
MASTER_FILE = 'master.csv'
MASTER_NODUPLS = 'master_NODUPLS.csv'
MASTER_NODUPLS_FILTERED =  'master_NODUPLS_FILTERED.csv'


def handle_error(function):
    """
    Exception handling decorator
    """
    def workout_problems(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print "\nEXCEPTION encountered: {}\n".format(e)
            print traceback.format_exc()
            return None
    return workout_problems

def get_csv_files(input_dir, suffix=".csv"):
    """
    Scan the input directory and return a list containing all the .csv files
    found there.

    :rtype: list
    :return: list containing the csv files in input_dir (full path)
             [] - on error
    """
    try:
        filenames = os.listdir(input_dir)
        return [os.path.join(input_dir, filename) for filename in filenames
                if filename.endswith(suffix)]
    except:
        return []

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

@handle_error
def add_cols(input_file):
    """
    Parse file name and add four columns to the file with the parsed info
    
    :rtype: str
    :return: absolute path to modified file or
             None - error
    """
    input_file_base = os.path.basename(input_file) 
    input_file_name, input_file_extn = os.path.splitext(input_file_base)
    output_file = input_file_name+'_COLS_ADDED.csv'
    input_file_name, input_file_extn = os.path.splitext(input_file_base)
    new_col_vals = input_file_name.split('_')
    if len(new_col_vals) < 4:
        raise Exception('File name \'{}\' does not have expected format.'.format(input_file))
    new_col_vals[2] = new_col_vals[2].replace('Pass ', '')

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
    return os.path.abspath(output_file)

@handle_error
def merge_files(input_files, output_file):
    """
    Scan input dir and merge all csv files found into a master spreadsheet

    :type input_files: list of str
    :param input_files: A list of files to be merged. All files must exist,
                        otherwise this function will return an error

    :type output_file: str
    :param output_file: desired path and name of output file

    :rtype: str
    :return: absolute path to resulting file on success 
             None - error
    """
    with open(output_file, 'w') as fout:
        first_file = input_files[0]
        with open(first_file) as first_in:
            for line in first_in:
                fout.write(line)
        for in_file in input_files[1:]:
            with open(in_file) as fin:
                fin.next()
                for line in fin:
                    fout.write(line)
    return os.path.abspath(output_file)

@handle_error
def remove_duplicates(input_file, output_file):
    """
    Remove lines with the same Name entry in input file 
    and save new file as output_file

    :type input_file: str
    :param input_file: file to remove duplicates from

    :type output_file: str
    :param output_file: desired path and name of output file

    :rtype: str
    :return: absolute path to resulting file on success 
             None - error
    """
    with open(input_file, 'r') as in_file:
        with open(output_file, 'w') as out_file:
            reader = csv.reader(in_file)
            writer = csv.writer(out_file)
            seen = set() 
            for line in reader:
                name = line[4].strip('"')
                if name in seen: 
                    continue 
                seen.add(name)
                writer.writerow(line)
    return os.path.abspath(output_file)

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

@handle_error        
def filter_blacklist(input_file, output_file, blacklist_file):
    """
    Remove entries in input_file that have names specified in the blacklist.
    Save the new file as output_file.

    :type input_file: str
    :param input_file: file to remove blacklisted entries from

    :type output_file: str
    :param output_file: desired path and name of output file

    :type output_file: str
    :param output_file: file that contains blacklisted names

    :rtype: str
    :return: absolute path to resulting file on success 
             None - error
    """
    with open(blacklist_file) as black_handle:
        black_handle.next()
        black_list = [line.strip() for line in black_handle]
    with open(input_file) as in_handle:
        with open(output_file, 'w') as out_handle:
            reader = csv.reader(in_handle)
            writer = csv.writer(out_handle)
            for line in reader:
                name = line[4]
                if not_on_blacklist(name, black_list):
                    writer.writerow(line)
    return os.path.abspath(output_file)

def csv_worker(input_dir, blacklist_file, output_dir=None):
    """
    Function that adds the 4 columns to all files in input_dir,
    merges them in a master file, removes duplicates and filters
    the blacklisted entries.

    :type input_dir: str
    :param input_dir: Valid path to input files

    :type blacklist_file: str
    :param blacklist_file: file containing names to be removed from
                           the master file

    :type output_dir: str
    :param output_dir: directory to write output files to.
                       Optional argument - if not specified, CWD is used

    :rtype: tuple: (str, str, str)
    :return: tuple containing full path and filename for:
             1. master file 
                or None in case of error 
             2. master file with duplicate lines removed
                or None in case of error
             3. master file with duplicates removed and filtered against blacklist
                or None in case of error
    """
    input_files = get_csv_files(input_dir)
    if not input_files:
        print "Error: Failed gathering input files from path: {}".format(
            input_dir)
        exit(1)
    files_list = [add_cols(input_file) for input_file in input_files]
    if None in files_list: exit(1)
    # create master file
    master_csv = "master.csv"
    if output_dir:
        if not os.path.isdir(output_dir):
            print "WARNING:Output dir '{}' does not exist. Using cwd".format(
                output_dir)
        else:    
            master_csv = os.path.join(output_dir, master_csv)
    master_csv = merge_files(files_list, master_csv)
    output_path = os.path.dirname(master_csv)
    if not master_csv: exit(1)
    # remove duplicates
    nodup_master = os.path.join(output_path, MASTER_NODUPLS)
    nodup_master = remove_duplicates(master_csv, nodup_master)
    if not nodup_master: exit(1)
    # filter blacklist
    filtered_nodup = os.path.join(output_path, MASTER_NODUPLS_FILTERED)
    filtered_nodup = filter_blacklist(nodup_master, filtered_nodup, blacklist_file)
    if not filtered_nodup: exit(1)
    return (master_csv, nodup_master, filtered_nodup)
    
if __name__ == "__main__":
    print csv_worker('../in/', '../BLACKLIST.csv', 'out')

