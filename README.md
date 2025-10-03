Diverse Projects

The scripts that I post here are diverse in nature and involve specific tests or projects that are unrelated to bigger projects.

The first script here is about searching PDF files for 1 or more keywords and making lists of these.
It works fine for simple PDF files generated from Word documents that were converted to PDF documents or PDF files created from Webpages.
PDF documents from publishers can not be searched so easily as they have a great variety of information in them that does not easily allow for searching through them using the tool.

The second script is intended to process Payment Institutions Register data from the European Banking Association. It is based on a full register downloaded json file from the website https://euclid.eba.europa.eu/register/pir/disclaimer . Important: I tested the script with two full downloads, one from 2021 and one from 2023. It took the script 5 hours to process the first file. The second file had information on significantly more Payment Entities compared to the first file: approx. 258.000 compared to 184.000 in 2021. The program needed 11 hours to process the second file. Processing speed may vary depending on the hardware+software of the computer used.

The third script compares the contents of two folders (provided by you) and generates an overview of files that are most likely the same in both folders. The comparison is made on both file names as well as the file hash (fingerprint). If no files are the same, no overview is created. An overview result will be exported as a csv file.

The fourth script can be used to collect ISBN book numbers from an Excel file and have publisher data collected (if possible) from Google Books using the API. It returns a text file with matched items. I made a new version of this script (v2) which does not first download the Google data as Json files but instead, immediately processes the data. The first is better if you are not sure the Google books data is processed well/correctly as you can view the original files also afterwards. The second prevents saving unnecessary data, i.e. when you are confident the data is processed correctly. 

The Fifth script makes it possible to automatically search for top 10 Google search results using an Excel file as input. The Excel file should contain a column with (in each cell) a list of keywords or search terms. To avoid Google considering the program to be a bot, I built in a random number of seconds between searches. Warning: the program uses a Google-search library that uses a Python resource that is deprecated in Python 3.12 and higher.  

The Sixth script is an example script that allows you to download (freely) up to 365 days of EUR exchange rate data for crypto coins that are available through CoinGecko. You need to register first, create your public API Key and then set up a config.py file with that Key.
