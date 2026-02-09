# Generate a RIS type files from a list from an Excel file for the Learning Lists
# RIS Reading lists files are based on ISBN and DOI from file
# https://support.talis.com/hc/en-gb/articles/17338816364189-Mapping-RIS-fields-to-Talis-Aspire
# The minimum required for a valid RIS record to be imported is:
# a type (TY), a title (T1, TI, BT or CT) and an end-of-record marker (ER) plus either DOI or ISBN.
#
# Author: Mark Bruyneel
#
# Date: 2025-09-02
# Version: 3.1
# Created using Python version 3.10
#
# Re-use note: Make sure to change folder names that are relevant to your computer

import requests
import re
import pandas as pd  # version 2.2.3
# To catch errors, use the logger option from loguru
from loguru import logger #version 0.7.2
# Also needed to get the run time of the script
from datetime import datetime #version 5.5
import time
import os

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

logger.add(r'U:\Werk\OWO\AIP\Werkproces\RIS_Reading_lists_test.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")
@logger.catch()

def main():
    # Get the file
    # Provide the file name and location for which to look up data
    excelfile = input('Please provide the location and name of the Excel file.\nExample: C:\\temp\keyword_list.xlsx \n')
    Pubs = pd.read_excel(f'{excelfile}', sheet_name='Sheet1', converters={'ISBN':str})
    # Keep part of the list with essential data:
    Publication_list = Pubs[['Course code', 'ISBN', 'DOI', 'Title']]

    # Create separate lists for if a DOI is available
    Pubs_DOI = Publication_list.dropna(subset=['DOI']).copy()

    # Remove existing 'ris files before generating new ones
    mydir = 'U:\Werk\OWO\AIP\Werkproces\\'
    filelist = [f for f in os.listdir(mydir) if f.endswith(".ris")]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

    # Add list of DOI codes to ris files if there is an ISBN or not. DOI has preference

    # replace codes if these occur. Some of them are irregular white spaces.
    # Maybe other replaces needed later? Unicode codes are the issue from copying?
    Pubs_DOI['Title'] = Pubs_DOI['Title'].str.replace('\u2003', '')
    Pubs_DOI['Title'] = Pubs_DOI['Title'].str.replace('\u2010', '')
    Pubs_DOI['Title'] = Pubs_DOI['Title'].str.replace('\u202f', '')
    Pubs_DOI['Title'] = Pubs_DOI['Title'].str.replace('\u2010', '')
    Pubs_DOI['Title'] = Pubs_DOI['Title'].str.replace('\u2011', '')

    # Work with a copy
    Pubs_DOI_new = Pubs_DOI.copy()

    # Remove duplicates from the full table
    Pubs_DOI_new = Pubs_DOI_new.drop_duplicates()

    # Create a list of DOI strings to search for, using the DOI website, to check validity
    # Make a list of the DOI codes that need to be looked up based on the Excel file
    Pubs_DOI_new_original = Pubs_DOI_new['DOI'].tolist()

    # create a list of unique DOI strings to check
    # Remove duplicates from the list. To do this, use the dictionary option which automatically does it
    # as dictionaries cannot have duplicates, and then immediately turn it into a list again
    DOI_list = list(dict.fromkeys(Pubs_DOI_new_original))

    # Perform the check for each DOI in the DOI list
    DOI_Listsize = len(DOI_list)
    # logger.debug(f'Nr. of DOI strings to search: ' + str(DOI_Listsize) + '\n')

    # https://www.doi.org/the-identifier/resources/factsheets/doi-resolution-documentation
    # Future items to be aware of ??:
    # No DOI found example result:
    # Response: {'responseCode': 102, 'message': 'Empty handle invalid'}
    #
    # Faulty DOI example result:
    # item = '10.1177/1529100617727266Clark'
    # Response: {'responseCode': 100, 'handle': '10.1177/1529100617727266Clark'}
    headers = {'Accept': 'application/json'}

    # Loop through the list to get search results
    nd = 0
    result = pd.DataFrame()
    response_n = []
    DOI = []
    while nd < DOI_Listsize:
        if DOI_list[nd] == 'nan':
            res = 'nan'
            doi = DOI_list[nd]
        elif DOI_list[nd] == '':
            res = 'nan'
            doi = DOI_list[nd]
        else:
            logger.debug(f'Searching DOI string: ' + str(nd+1) + ' of ' + str(DOI_Listsize))
            r = requests.get('https://doi.org/api/handles/' + str(DOI_list[nd]), headers=headers)
            test_result = r.json()
            try:
                res = test_result['responseCode']
            except:
                res = 'nan'
            try:
                doi = test_result['handle']
            except:
                doi = DOI_list[nd]
        response_n.append(res)
        DOI.append(doi)
        nd = nd + 1
    interim_table = {'Response': response_n}
    test_table = pd.DataFrame(interim_table)
    test_table['DOI'] = DOI
    Final_Table = pd.concat([result, test_table], ignore_index=True)

    # Merge Search result DOI table "Final_Table" with original DOI table
    Final_DOI_list = pd.merge(Pubs_DOI, Final_Table, how='outer', on=['DOI'])

    # Keep only result where DOI was correct = response is 1
    Table_Correct_DOI = Final_DOI_list[Final_DOI_list['Response'] == 1]
    # Remove ISBN field as this is no longer necessary
    New_table_correct_DOI = Table_Correct_DOI.drop(['ISBN'], axis=1)
    # Remove duplicates from this table
    New_table_correct_DOI = New_table_correct_DOI.drop_duplicates()
    # print(New_tale_correct_DOI)

    nr_of_doi_rows = len(New_table_correct_DOI)
    doirownr = 0
    doicolnra = 0
    doicolnrb = 1
    Titlec = 2
    while doirownr < nr_of_doi_rows:
        File_Name = f"{New_table_correct_DOI.iloc[doirownr, doicolnra]}.ris"
        path = os.path.join(mydir, File_Name)
        if os.path.exists(path):
            f = open(path, 'a')  # 'r' for reading and 'w' for writing, 'x' for creating
            f.write('\n\n')
            f.write('TY  - JOUR')
            f.write('\nTI  - ' + str(New_table_correct_DOI.iloc[doirownr, Titlec]))
            f.write('\nDO  - ' + str(New_table_correct_DOI.iloc[doirownr, doicolnrb]))  # Write inside file
            f.write('\nER  - ')
            f.close()
        else:
            f = open(path, 'x')  # 'r' for reading and 'w' for writing, 'x' for creating
            f.write('TY  - JOUR')
            f.write('\nTI  - ' + str(New_table_correct_DOI.iloc[doirownr, Titlec]))
            f.write('\nDO  - ' + str(New_table_correct_DOI.iloc[doirownr, doicolnrb]))  # Write inside file
            f.write('\nER  - ')
            f.close()
        doirownr = doirownr + 1

    # Now part 2: for all other records in Publication_list that have no DOI (or an incorrect one,
    # get those that have an ISBN, check them for correctness and add records to existing ris files
    # or generate new ris files for courses when needed

    ISBN_start_list = pd.merge(Publication_list, New_table_correct_DOI, how='outer', on=['DOI'])

    # Remove matched records and records which have no ISBN
    No_correct_DOI = ISBN_start_list[ISBN_start_list['Response'] != 1]
    Pubs_ISBN1 = No_correct_DOI.dropna(subset=['ISBN']).copy()
    # Turn column with ISBN or DOI codes into string to search later
    Pubs_ISBN = Pubs_ISBN1.astype(str)

    # Remove added .0 from each ISBN that was added by importing
    # The actions depend on the source file and may change if the source is different
    # Pubs_R_new['ISBN'] = Pubs_R_new['ISBN'].str.replace('.0', '')
    Pubs_ISBN['ISBN'] = Pubs_ISBN['ISBN'].str.replace('.', '')
    Pubs_ISBN['ISBN'] = Pubs_ISBN['ISBN'].str.replace('+', '')
    Pubs_ISBN['ISBN'] = Pubs_ISBN['ISBN'].str.replace('E', '')

    # Make a list of the ISBN codes that need to be looked up based on the Excel file
    ISBN_list_original = Pubs_ISBN['ISBN'].tolist()

    # Remove the item syllabus if it occurs in the list
    try:
        ISBN_list_original.remove('syllabus')
    except ValueError:
        pass

    # Create an empty list to store unique ISBNs = to remove duplicate ISBNs
    # This because you need to only check unique ISBNs for validity
    ISBN_list = []
    # Iterate through each value in the list 'a'
    for book in ISBN_list_original:
        # Check if the value is not already in 'ISBN_list'
        if book not in ISBN_list:
            # If not present, append it to 'ISBN_list
            ISBN_list.append(book)

    # Perform the check for each ISBN in the ISBN list
    Listsize = len(ISBN_list)

    # The ISBN strings originally were harvested
    # using Regex string searches in PDF documents.
    n = 0
    vISBN_list = []
    while n < Listsize:
        isbn_c = ISBN_list[n]
        print('check isbn: ', isbn_c)
        # Remove non ISBN digits, then split into a list
        chars = list(re.sub("[- ]|^ISBN(?:-1[03])?:?", "", isbn_c))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last = chars.pop()
        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x, y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x, y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"

        if (str(check) == last):
            vISBN_list.append(isbn_c)
        else:
            pass
        n = n + 1

    # Merge the valid list with the original list of ISBNs for all courses
    # First make a Dataframe for the valid ISBN list
    Valid_ISBN_df = pd.DataFrame(vISBN_list, columns=['ISBN'])
    Valid_ISBN_df['Valid'] = 'True'

    # Now use merge to get the new Dataframe with valid ISBN codes based on the original ISBN list
    Final_ISBN_list = pd.merge(Pubs_ISBN, Valid_ISBN_df, how='outer', on=['ISBN'])
    Final_ISBN_list = Final_ISBN_list.drop_duplicates()
    # Rename column to original name
    Final_ISBN_list = Final_ISBN_list.rename(columns={'Course code_x': 'Course code'})
    sorted_ISBN_listi = Final_ISBN_list.sort_values(by=['Course code'])
    # Remove invalid ISBN from the file
    sorted_ISBN_list = sorted_ISBN_listi[sorted_ISBN_listi.Valid == 'True']
    sorted_ISBN_list = sorted_ISBN_list.drop_duplicates()
    sorted_ISBN_list = sorted_ISBN_list.rename(columns={'Title_x': 'Title'})
    sorted_ISBN_list = sorted_ISBN_list.drop(['DOI'], axis=1)

    # Add Ris files for correct ISBN records or append to existing ris files
    number_of_rows = len(sorted_ISBN_list)
    rownr = 0
    colnra = 0
    colnrb = 1
    title = 2

    while rownr < number_of_rows:
        File_Name = f"{sorted_ISBN_list.iloc[rownr, colnra]}.ris"
        path = os.path.join(mydir, File_Name)
        if os.path.exists(path):
            f = open(path, 'a')  # 'r' for reading and 'w' for writing, 'x' for creating
            f.write('\n\n')
            f.write('TY  - BOOK')
            f.write('\nTI  - ' + str(sorted_ISBN_list.iloc[rownr, title]))
            f.write('\nSN  - ' + str(sorted_ISBN_list.iloc[rownr, colnrb]))  # Write inside file
            f.write('\nER  - ')
            f.close()
        else:
            f = open(path, 'x')  # 'r' for reading and 'w' for writing, 'x' for creating
            f.write('TY  - BOOK')
            f.write('\nTI  - ' + str(sorted_ISBN_list.iloc[rownr, title]))
            f.write('\nSN  - ' + str(sorted_ISBN_list.iloc[rownr, colnrb]))  # Write inside file
            f.write('\nER  - ')
            f.close()
        rownr = rownr + 1

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