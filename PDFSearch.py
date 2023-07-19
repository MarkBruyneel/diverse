# Script to search for one or more keywords in a set of PDF files
# Author: Mark Bruyneel
# Date: 2023-07-06

from pathlib import Path
from loguru import logger
from datetime import datetime
import time
import os
import pandas as pd
import PyPDF2
# PyPDF2 requires dependent library for secure PDF files: PyCryptodome

# Show all data in screen
pd.set_option("display.max.columns", None)

# Create date variable for filenames
runday = str(datetime.today().date())

# Create a date + time for logging start
now = str(datetime.now())
nowt = time.time()

logger.add(r'U:\Werk\Data Management\Python\\Files\output\PDF_Search.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")
@logger.catch()

def main():
    # Determine the number of terms to be searched
    termnumber = input('How many keywords do you want?\n')
    termnumber = int(termnumber)

    # Now create the termlist by input of search terms
    termlist = []
    while termnumber != 0:
        Newterm = input('Add a new search term to the list: ')
        termlist.append(Newterm)
        termnumber = termnumber - 1

    # Establish location and files with data. Put the filenames in a table
    searchpath = input('What is the location of the PDF files on the computer (folder)?\n')
    dir_path = searchpath

    # Establish what type of documents are to be searched
    document_type = input('What type of PDF files are searched ? Example: papers\n')

    # Start search indicator
    logger.debug('Start search through the PDF files at: ' + now)

    # Get list of all files only in the given directory
    document = lambda x: os.path.isfile(os.path.join(dir_path, x))
    document_list = filter(document, os.listdir(dir_path))

    # Create a list of files in directory along with the size
    document_newlist_g = [
        (f, os.stat(os.path.join(dir_path, f)).st_size)
        for f in document_list
    ]

    # Create a DataFrame with the list as input
    document_newlist = pd.DataFrame(document_newlist_g, columns=['Filename', 'File_size'])
    # Limit to just the PDF files in the list
    newlist = document_newlist[document_newlist['Filename'].str.contains('.pdf')]
    # Exclude possible empty files with no data / text
    finallist = newlist[newlist['File_size']>100].copy()
    filenrsf = finallist.shape[0]
    print('Number of PDF files to be searched: ', filenrsf)

    result_list = []
    for filename in finallist['Filename'].values:
        print('Processing file: ', filename)
        # For the PyPDF2 package I need to indicate strict=False because of a bug
        reader = PyPDF2.PdfReader(searchpath + filename, strict=False)
        for page_number in range(0, len(reader.pages)):
            page = reader.pages[page_number]
            page_content = page.extract_text()
            for search_term in termlist:
                if search_term in page_content:
                    result = {
                        "page": page_number,
                        "content": filename,
                        "keyword": search_term
                    }
                    result_list.append(result)

    # Create a group based on papers and search term count
    if len(result_list) < 100:
        print('Keyword(s) were not found in the PDF files.')
        logger.debug('Keyword(s) were not found in the PDF files.')
    else:
        result_list_new = pd.DataFrame.from_dict(result_list)
        result_list_new.to_csv(f'U:\Werk\Data Management\Python\\Files\output\{document_type}_TermSearch_{runday}.csv', encoding='utf-8')
        result_temp = result_list_new.groupby(['content', 'keyword'], as_index=False).count()
        print('Paper overview:\n', result_temp.head())
        result_temp.to_csv(f'U:\Werk\Data Management\Python\\Files\output\{document_type}_term_count_{runday}.csv', encoding='utf-8')

    logger.debug('Location of PDF files / Folder searched : ' + searchpath)
    # Logging of script run:
    end = str(datetime.now())
    logger.debug('Search through the PDF files completed at: ' + end)
    duration_s = (round((time.time() - nowt),2))
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