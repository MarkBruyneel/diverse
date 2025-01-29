# Publishers tool to be able to augment AIP data from Canvas with
# publisher data from Google using the Google API
# Author: Mark Bruyneel
#
# Date: 2024-12-18
# Version: 1.0
# Created using Python version 3.10
#
# Re-use note: Make sure to change folder names that are relevant to your computer

import requests #version 2.32.3
import sys
import os
import re
import pandas as pd #version 2.2.3
import json
# To catch errors, use the logger option from loguru
from loguru import logger #version 0.7.2
# Also needed to get the run time of the script
from datetime import datetime #version 5.5
import time
from pathlib import Path #version 1.0.1

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

logger.add(r'U:\Werk\OWO\AIP\AIP_Publisher_v2_Search.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")
@logger.catch()

def main():
    excelfile = input('Please provide the location and name of the Excel file.\nExample: C:\\temp\keyword_list.xlsx \n')
    sh_name = input('Please provide the exact sheet name that has the ISBN column: \n')
    Pubs = pd.read_excel(f'{excelfile}', sheet_name=sh_name)
    # Keep part of the list with essential data:
    Publication_list = Pubs[['ISBN', 'Publisher']].copy()

    # Keep DataFrame where ISBN is available and where Publisher is not available'
    Pubs_R_new1 = Publication_list.dropna(subset=['ISBN'])
    Pubs_R_new = Pubs_R_new1.loc[Pubs_R_new1['Publisher'].isnull()]
    # Turn column with ISBN codes into string to search later
    Pubs_R_new = Pubs_R_new.astype(str)
    # Remove added .0 from each ISBN that was added by imporing
    Pubs_R_new['ISBN'] = Pubs_R_new['ISBN'].str.replace('.0', '')

    # Make a list of the ISBN codes that need to be looked up based on the Excel file
    ISBN_list_original = Pubs_R_new['ISBN'].tolist()
    # Remove the item syllabus if it occurs in the list
    try:
        ISBN_list_original.remove('syllabus')
    except ValueError:
        pass

    # Create an empty list to store unique books
    ISBN_list = []
    # Iterate through each value in the list 'a'
    for book in ISBN_list_original:
        # Check if the value is not already in 'ISBN_list'
        if book not in ISBN_list:
            # If not present, append it to 'ISBN_list
            ISBN_list.append(book)

    # Create an output folder if it doesn't exist
    Path('U:\Werk\OWO\AIP\Output').mkdir(parents=True, exist_ok=True)

    # Get the data for each publication in the ISBN list
    Listsize = len(ISBN_list)
    print('\n Number of ISBN codes: ', Listsize, '\n')

    # Check if the ISBN is correct or not. The ISBN strings originally were harvested
    # using Regex string searches in PDF documents.
    n = 0
    vISBN_list = []
    while n < Listsize:
        isbn_c = ISBN_list[n]
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
            print("\nValid ISBN: ", isbn_c)
            vISBN_list.append(isbn_c)
        else:
            print("\nInvalid ISBN: ", isbn_c)
        n = n + 1

    valid_isbn = len(vISBN_list)
    Len_valid = str(valid_isbn)
    print('\n Number of valid ISBN codes: ', Len_valid, '\n')
    print('All isbns: ', vISBN_list)

    # Create variables for DataFrame
    Original_ISBN = []
    BookListPublisher = []
    ISBN_book = []

    Publisher_Book_Table = pd.DataFrame()

    i = 0
    while i < valid_isbn:
        isbn = vISBN_list[i]
        print('Attempting to retrieve data for nr. ', i, ' of ', Len_valid, ' (ISBN): ', isbn)
        # ...?q=isbn:0262527359, the results you get are the books that have this same isbn only
        # ...?q=0262527359, the results you get are the books that have any instance of this number in the record
        # fields of any book. It can be either in editions isbn array or any other, this query will search all
        # fields for matching results whereas the former query will only search isbn for matching results
        if len(isbn) > 12:
            url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'+isbn
        else:
            url = 'https://www.googleapis.com/books/v1/volumes?q='+isbn
        r = requests.get(url)
        data = r.json()

        # Get size of file to make sure it contains data
        size = sys.getsizeof(json.dumps(data))

        if size <= 120:
            logger.debug(f'Nothing found for ISBN ' + isbn)
        else:
            logger.debug(f'Copying and adding publisher data for ISBN ' + isbn)
            # Process data from Google and create DataFrame
            isbn_length = len(isbn)
            if len(data['items']) < 2:
                try:
                    # Test if the publisher field is missing
                    pub = data['items'][0]['volumeInfo']['publisher']
                except KeyError:
                    pub = "None"
                try:
                    # Test if a field is available with an ISBN code
                    testlenid = len(data['items'][0]['volumeInfo']['industryIdentifiers'])
                except KeyError:
                    testlenid = 0
                if testlenid < 2:
                    isbn_id = "None"
                else:
                    try:
                        isbn_id = data['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
                        iid_len = len(isbn_id)
                        if isbn_length > 10:
                            if iid_len < 13:
                                isbn_id = data['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
                            else:
                                isbn_id = data['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
                        else:
                            if iid_len < 13:
                                isbn_id = data['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
                            else:
                                isbn_id = data['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
                    except KeyError:
                        isbn_id = "None"
                BookListPublisher.append(pub)
                ISBN_book.append(isbn_id)
                Original_ISBN.append(isbn)
            else:
                nr_items = len(data['items'])
                startnr = 0
                while startnr < nr_items:
                    try:
                        pub = data['items'][startnr]['volumeInfo']['publisher']
                    except KeyError:
                        pub = "None"

                    if 'industryIdentifiers' in data['items'][startnr]['volumeInfo']:
                        testlenid = len(data['items'][startnr]['volumeInfo']['industryIdentifiers'])
                        if testlenid < 2:
                            isbn_id = "None"
                        else:
                            try:
                                isbn_id = data['items'][startnr]['volumeInfo']['industryIdentifiers'][1][
                                    'identifier']
                                iid_len = len(isbn_id)
                                if isbn_length > 10:
                                    if iid_len < 13:
                                        isbn_id = data['items'][startnr]['volumeInfo']['industryIdentifiers'][0][
                                            'identifier']
                                    else:
                                        isbn_id = data['items'][startnr]['volumeInfo']['industryIdentifiers'][1][
                                            'identifier']
                                else:
                                    if iid_len < 13:
                                        isbn_id = data['items'][startnr]['volumeInfo']['industryIdentifiers'][1][
                                            'identifier']
                                    else:
                                        isbn_id = data['items'][startnr]['volumeInfo']['industryIdentifiers'][0][
                                            'identifier']
                            except KeyError:
                                isbn_id = "None"
                        BookListPublisher.append(pub)
                        ISBN_book.append(isbn_id)
                        Original_ISBN.append(isbn)
                        startnr = startnr + 1
                    else:
                        startnr = startnr + 1
            book_data_table = {'ISBN': ISBN_book}
            book_table = pd.DataFrame(book_data_table)
            book_table['Publisher'] = BookListPublisher
            book_table['Original_ISBN'] = Original_ISBN
        print('Next API request in 10 sec...\n')
        time.sleep(10)
        i = i + 1

    Publisher_Book_Table = pd.concat([Publisher_Book_Table, book_table], ignore_index=True)

    # Remove rows where the ISBN is not available or Publisher was not there
    Publisher_Book_Table = Publisher_Book_Table[Publisher_Book_Table['ISBN'].str.contains('None') == False]
    Publisher_Book_Table = Publisher_Book_Table[Publisher_Book_Table['Publisher'].str.startswith('None') == False]
    # Drop duplicates
    Publisher_Book_Table = Publisher_Book_Table.drop_duplicates()

    # Add a new column with the original ISBN as per the Excel file to compare with the one from Google.
    # The ISBN should be used to match with the original ISBN in the source Excel file.
    # This, to avoid matching on a changed ISBN from the Json file that is returned
    Publisher_Book_Table['Match_ISBN'] = Publisher_Book_Table['Original_ISBN'].str.replace('-', '')

    # Drop columns where the original ISBN does not match the found ISBN
    Publisher_Book_Table.drop(Publisher_Book_Table[Publisher_Book_Table['Match_ISBN'] != Publisher_Book_Table['ISBN']].index, inplace=True)

    # Export end result
    Publisher_Book_Table.to_csv(f'U:\Werk\OWO\AIP\Output\Book_list' + runday + '.txt', sep='\t' ,encoding='utf-8')

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