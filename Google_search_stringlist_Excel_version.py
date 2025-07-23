# Python program to use Google to get top 10 for a string list using an excel file
# Author: Mark Bruyneel
#
# Date: 2025-07-21
# Version: 1.0
# Created using Python version 3.11 and 3.10

# import
import warnings
from googlesearch import search # goodlesearch-python versie 1.3.0
from loguru import logger  # version 0.7.2
# Also needed to get the run time of the script
from datetime import datetime  # version 5.5
import time
import random
import numpy as np
import pandas as pd  # version 2.2.3
import shutil
from pathlib import Path

# Program requires Python 3.11 or lower:
# Important note on using the googlesearch import library:
# https://github.com/mu-editor/mu/issues/2485
# pkg_resources is deprecated and removed in Python 3.12
# Use of pkg_resources is deprecated in favor of importlib.resources, importlib.metadata
# and their backports (importlib_resources, importlib_metadata). Some useful APIs are
# also provided by packaging (e.g. requirements and version parsing). Users should refrain
# from new usage of pkg_resources and should work to port to importlib-based solutions.
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Show all data in screen
pd.set_option("display.max.columns", None)

# Create year and date variable for filenames etc.
today = datetime.now()
year = today.strftime("%Y")
runday = str(datetime.today().date())
runyear = str(datetime.today().year)

# Create a date + time for file logging
now = str(datetime.now())
nowt = time.time()

# Generate a list of numbers for time.sleep if needed to make sure that Google
# searches are not automatically
li = random.choices(range(1, 100), k=50)

logger.add(r'U:\Werk\Data Management\Python\Files\output\Google_Text_Search_test.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")

@logger.catch()
def main():
    # Provide the file name and location for which to look up data
    excelfile = input('Please provide the location and name of the Excel file.\nExample: C:\\temp\keyword_list.xlsx \n')
    sh_name = input('Please provide the exact sheet name that has the data: \n')
    ss_name = input('Please provide the column name: \n')
    file = pd.read_excel(f'{excelfile}', sheet_name=sh_name)

    # Show part of the file used to search
    print('Partial list provided:\n', file.head(), '\n')
    # Keep part of the list with essential data:
    string_list_full = file.copy()
    # remove duplicate strings
    search_list = string_list_full.drop_duplicates()

    # Now generate a list of strings it needs to look up
    filename_list = search_list[ss_name].tolist()
    # Remove duplicates from the list. To do this, use the dictionary option which automatically does it
    # as dictionaries cannot have duplicates, and then immediately turn it into a list again
    filename_list = list(dict.fromkeys(filename_list))

    # How many items to search for on Google = based on list size
    ListSize = len(filename_list)
    logger.debug(f'Nr. of strings to search: ' + str(ListSize) +'\n')
    List_start = 0

    # Loop through the list to get search results
    Strings_searched = []
    Links_result = []
    Titles_result = []
    Descriptions_result = []

    while List_start < ListSize:
        if filename_list[List_start] == 'nan':
            pass
        elif filename_list[List_start] == '':
            pass
        else:
            # Select a random number of list li
            randnr = random.choice(li)
            listnr = List_start + 1
            logger.debug(f'Search string ' + str(listnr) + ' of ' + str(ListSize) + ': ' + str(filename_list[List_start]), '\n')
            response = search(filename_list[List_start], sleep_interval=randnr, num_results=10, unique=True, advanced=True)
            for result in response:
                Strings_searched.append(filename_list[List_start])
                Titles_result.append(result.title)
                Links_result.append(result.url)
                Descriptions_result.append(result.description)
        List_start = List_start + 1

    Google_link_result_temp = pd.DataFrame(np.column_stack([Titles_result, Links_result, Descriptions_result, Strings_searched]), columns=['Title', 'URL', 'Description', 'String_searched'])

    # Show part of the result
    print('Table result:\n', Google_link_result_temp.head())
    # Remove records with no result
    Google_link_result_temp['Title'].astype(bool)
    Google_link_result = Google_link_result_temp[Google_link_result_temp['Title'].str.strip().astype(bool)]

    # Export the result
    Google_link_result.to_csv(f'U:\Werk\Data Management\Python\Files\output\Google_Stringlist_top10_result_list_' + runday + '.txt', sep='\t', encoding='utf-16')

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

# start main
if __name__ == "__main__":
    main()