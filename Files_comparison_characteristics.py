# This script is intended to process files in two folders/directories that you indicate.
# It will store the characteristics of the files. It will then see if there are duplicate files
# in both folders and indicate which they are (most likely) and export the result.
#
# Mark Bruyneel
# 2024-09-21
# Script version 1.1

import os
import sys
import pandas as pd
import numpy as np
from loguru import logger
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Show all data in screen
pd.set_option("display.max.columns", None)
# Create year and date variable for filenames etc.
today = datetime.now()
year = today.strftime("%Y")
runday = str(datetime.today().date())
runyear = str(datetime.today().year)
timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

# Create a date + time for file logging
now = str(datetime.now())
nowt = time.time()

# Function to exit program if event occurs
def exit_program():
    print("Exiting the program...")
    sys.exit(0)

# Function to get a more (human) readable date and time
def rdbl_time(NewTime):
    dt = datetime.fromtimestamp(NewTime)  # conver from epoch timestamp to datetime
    return datetime.strftime(dt, "%Y %b %d (%a), %H:%M:%S")

# Function that calculates the MD5 Hash of a file in chunks of 4 kilobytes. Hashes are the output of a hashing algorithm
# like MD5 (Message Digest 5) or SHA (Secure Hash Algorithm). These algorithms essentially aim to produce a unique,
# fixed-length string – the hash value, or “message digest” – for any given piece of data or “message”. As every file on
# a computer is, ultimately, just data that can be represented in binary form, a hashing algorithm can take that data
# and run a complex calculation on it and output a fixed-length string as the result of the calculation. The result is
# the file’s hash value or message digest.
# In this case I chose to use MD5 over SHA1. MD5 generates a 128-bit hash result and is faster.
# SHA1 generates a 160-bit hash value and provides higher security, but it is slower.
def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

logger.add(r'C:\Temp\Files_comparison'+runday+'.log', backtrace=True, diagnose=True, rotation="100 MB", retention="12 months")
@logger.catch()

def main():
    # Step 1 Provide the folder names which have files that you wish to check for duplicates
    # Also make sure that the folders exist and the right input format is provided.
    # The folder path needs to end with a \ character
    while True:
        pathi1 = input('Provide the name of the two folders. Example folder name: c:\\temp\\ \nProvide the first folder name: \n')
        pathi2 = input('Provide the second folder name: \n')

        if (len(pathi1) < 3 or len(pathi2) < 3):
            print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
            print('\nBoth folder names require at least 3 characters. Please try again.\n')
        elif (len(pathi1) > 256 or len(pathi2) > 2563):
            print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
            print('\nFolder path names cannot exceed 256 characters (Windows default). Please try again.\n')
        else:
            last_char1 = pathi1[-1]
            last_char2 = pathi2[-1]
            second_char1 = pathi1[1]
            second_char2 = pathi2[1]
            third_char1 = pathi1[2]
            third_char2 = pathi2[2]
            example_character = '\\'
            example_character2 = ':'
            test1 = last_char1.find(example_character)
            test2 = last_char2.find(example_character)
            test3 = second_char1.find(example_character2)
            test4 = second_char2.find(example_character2)
            test5 = third_char1.find(example_character)
            test6 = third_char2.find(example_character)

            if not os.path.exists(pathi1) or not os.path.exists(pathi2):
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print("\nOne or both folder names provided do not exist or cannot be found. Please try again.\n")
                continue
            if not os.path.isdir(pathi1) or not os.path.isdir(pathi2):
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print("\nThe names provided are not folders. Please try again.\n")
                continue
            if (pathi1 == pathi2):  # are these folders the same
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print("\nComparison not possible: both folder names are the same. Please try again.\n")
                continue
            if (test1 < 0 or test2 < 0):
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print('\nBoth folder names require a \ at the end. Please try again.\n')
                continue
            if (test3 < 0 or test4 < 0):
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print('\nBoth folder names require a : as the second character. Please try again.\n')
                continue
            if (test5 < 0 or test6 < 0):
                print("\nFolder names you provided: " + pathi1 + " & " + pathi2)
                print('\nBoth folder names require a \ as the third character. Please try again.\n')
                continue
            break
    logger.debug(f'Folder names provided: \n Folder name 1:   ' + pathi1 + '\n Folder name 2:   ' + pathi2)

    # Step 2: Establish what files exist in both folders. Put the filenames in a table
    # and add the characteristics to two separate Dataframe. Include hash codes for
    # unique fingerprinting of files to compare on. Python 3 has the built in hashlib library.
    # Establish location and files with data. Put the filenames in a table
    # and add the date in the file name as data for the second column
    folder1 = pathi1
    folder2 = pathi2

    # Get lists of all files only in the given directories
    overviewlist1 = lambda x: os.path.isfile(os.path.join(folder1, x))
    files_list1 = filter(overviewlist1, os.listdir(folder1))
    overviewlist2 = lambda x: os.path.isfile(os.path.join(folder2, x))
    files_list2 = filter(overviewlist2, os.listdir(folder2))

    # Create a list of file characteristics for both folders
    # Remark: st_ctime is creation time on Windows computers
    data_of_files1 = [
        (f, os.stat(os.path.join(folder1, f)).st_size, rdbl_time(os.stat(os.path.join(folder1, f)).st_ctime), rdbl_time(os.stat(os.path.join(folder1, f)).st_mtime), calculate_md5(folder1+f), folder1)
        for f in files_list1
    ]
    data_of_files2 = [
        (f, os.stat(os.path.join(folder2, f)).st_size, rdbl_time(os.stat(os.path.join(folder2, f)).st_ctime), rdbl_time(os.stat(os.path.join(folder2, f)).st_mtime), calculate_md5(folder2+f), folder2)
        for f in files_list2
    ]

    # Create a table with the list as input
    folder_list1 = pd.DataFrame(data_of_files1, columns=['File_name', 'File_size', 'Created_on', 'Last_modified', 'File_hash', 'File_folder'])
    folder_list2 = pd.DataFrame(data_of_files2, columns=['File_name', 'File_size', 'Created_on', 'Last_modified', 'File_hash', 'File_folder'])

    # Compare columns between Dataframes and add yes/no if true
    # df1['isPresent'] = df1['UID'].isin(df2['UID'])
    # Compare both filenames and file hashes for both tables/Dataframes
    # The new variables contain True or False if a match is found
    folder_list1['MatchesHash'] = folder_list1['File_hash'].isin(folder_list2['File_hash'])
    folder_list1['MatchesName'] = folder_list1['File_name'].isin(folder_list2['File_name'])

    folder_list2['MatchesHash'] = folder_list2['File_hash'].isin(folder_list1['File_hash'])
    folder_list2['MatchesName'] = folder_list2['File_name'].isin(folder_list1['File_name'])

    # Create table Result containing matches
    #
    # Check for duplicates based on the first list in the second list
    folder1 = folder_list1.copy()
    result1 = folder1[(folder1['MatchesHash'] == True) | (folder1['MatchesName'] == True)]

    # Check for duplicates based on the second list in the first list
    folder2 = folder_list2.copy()
    result2 = folder2[(folder2['MatchesHash'] == True) | (folder2['MatchesName'] == True)]

    # Add the resulting matches together in a single resulting table
    result = pd.concat([result1, result2], axis=0)
    # Sort on Hash. This needs to be a string to do this
    result['File_hash'] = result['File_hash'].astype(str)
    result = result.sort_values(['File_hash','File_name'])

    if result.empty:
        logger.debug('No duplicate files found in folders.')
    else:
        dfsize = result.shape[0]
        dupnr = str(dfsize / 2)
        logger.debug('Possible duplicate files found. Amount: ' + dupnr)
        logger.debug('See for the result in: C:\Temp\..')
        result.to_csv(f'C:\Temp\Comparison_result_' + timestr + '.txt', sep='\t', encoding='utf-8')

    # Logging of script run:
    end = str(datetime.now())
    logger.debug('Processing started at: ' + now)
    logger.debug('Processing completed at: ' + end)
    duration_s = (round((time.time() - nowt), 2))
    if duration_s > 3600:
        duration = str(duration_s / 3600)
        logger.debug('Search took: ' + duration + ' hours.')
    elif duration_s > 60:
        duration = str(duration_s / 60)
        logger.debug('Search took: ' + duration + ' minutes.')
    else:
        duration = str(duration_s)
        logger.debug('Search took: ' + duration + ' seconds.')


if __name__ == "__main__":
    main()