# Tool to convert shorter CUSIP codes to the longer version.
# Cusip is a nine-character numeric or alphanumeric code that uniquely identifies
# a North American financial security for the purposes of facilitating clearing
# and settlement of trades.
# The CUSIP system is owned by the American Bankers Association (ABA) and is
# operated by FactSet Research Systems Inc.[4] The operating body, CUSIP Global
# Services (CGS), also serves as the national numbering agency (NNA) for North
# America, and the CUSIP serves as the National Securities Identification Number
# (NSIN) for products issued from both the United States and Canada. In its role
# as the NNA, CUSIP Global Services (CGS) also assigns all US-based International
# Securities Identification Numbers (ISINs).
# Background information: https://en.wikipedia.org/wiki/CUSIP
# Partially based on an original code by Paul Barendregt from 2009

# Author: Mark Bruyneel
# Version: 1.0
# Date: 2026-02-21

import sys
import string
from datetime import datetime
from loguru import logger #version 0.7.2

today = datetime.now()
runday = str(datetime.today().date())

# constants for calculating Cusip 9 codes
cusipchars = string.digits + string.ascii_uppercase + "*@#"
cusip2value = dict((ch, n) for n,ch in enumerate(cusipchars))
cusipweights = [1,2,1,2,1,2,1,2]

# Stops the program
def exit_program():
    print("Exiting the program...")
    sys.exit(0)

# Check if Cusip code is correct
def checksum(cusip):
	digits = [(w*cusip2value[ch]) for w,ch in zip(cusipweights, cusip)]
	cs = sum([(x%10+x//10) for x in digits]) % 10
	return str((10-cs)%10)

# Calculate cusip code digit 9 based on the first 8
def controlegetal_berekenen(self, kern):
    controlegetal = checksum(kern)
    cusip_heel = '%s%s' % (kern, controlegetal)
    return cusip_heel

# Writes result of a converted list to a file
def write_output(code_output):
    with open(f'U:\\cusip_list_converted_{runday}.txt', 'a') as output:
        output.write(str(code_output) + '\n')

@logger.catch()
def main():
    # What is the input going to be?
    choice = ''
    while choice not in ('1', '2', 'q'):
        print('This tool can convert Cusip 6 or 8 codes to full Cusip 9 codes\nN.B.: Cusip 6 codes will as a default be extended to 8 with: 10\nFor example, 24906P will become 24906P10\n ')
        choice = input('Do you wish to convert one code (1) or a list (2)?\nEnter q if you want to quit the program.\nPlease enter your choice (1 or 2 or q):')
        if choice == '1':
            # Create a loop in case someone wants to convert a couple of individual codes
            runanswer = ''
            while runanswer != 'no':
                runanswer = input('\nDo you want to convert a(nother) Cusip code (yes/no) ?')
                if runanswer == "yes":
                    choice_cusip_conversion = ''
                    while choice_cusip_conversion not in ('6', '8'):
                        choice_cusip_conversion = str(input('Provide a choice: convert a cusip 6 or 8 (6 / 8)'))
                        if choice_cusip_conversion == '6':
                            # Part to calculate based on a list of 6 character cusip codes
                            issue = str(input('Provide six digit Cusip code:'))
                            # Check code
                            if len(issue) < 6:
                                print(f'Too few number of characters (less then 6): {issue}')
                            elif len(issue) > 7:
                                print(f'Incorrect number of characters (More then 6) {issue}')
                            else:
                                print(f'Original input: {issue}')
                                volgnr = '10'
                                kern = (issue + volgnr)
                                cusip_heel = controlegetal_berekenen(volgnr, kern)
                                print(f'Full 9 digit Cusip: {cusip_heel}\n')
                        elif choice_cusip_conversion == '8':
                            # Part to calculate based on a list of 8 character cusip codes
                            issue = str(input('Provide eighth digit Cusip code:'))
                            # Check code
                            if len(issue) < 8:
                                print(f'Too few number of characters (less then 8): {issue}')
                            elif len(issue) > 8:
                                print(f'Incorrect number of characters (More then 8): {issue}')
                            else:
                                print(f'Original input: {issue}')
                                volgnr = issue[6:]
                                base_issue = issue[0-5]
                                kern = issue
                                cusip_heel = controlegetal_berekenen(volgnr, kern)
                                print(f'Full 9 digit Cusip: {cusip_heel}\n')
                        else:
                            logger.debug(f'Please enter a valid choice: 6 or 8')
                else:
                    logger.debug(f'Thank you for using the program.')
                    pass
        elif choice == '2':
            # Provide the file name and location for which to look up data
            textfile = input('Please provide the location and name of the Excel file.\nExample: C:\\temp\cusip_list.txt \n')
            with open(textfile) as file_in:
                lines = file_in.read().splitlines()
            logger.debug(f'Total number of codes: {len(lines)}')
            logger.debug(f'Working on converting codes ...')
            for code in lines:
                if len(code) == 6:
                    volgnr = '10'
                    kern = (code + volgnr)
                    cusip_heel = controlegetal_berekenen(volgnr, kern)
                    write_output(cusip_heel)
                elif len(code) == 8:
                    volgnr = code[6:]
                    kern = code
                    cusip_heel = controlegetal_berekenen(volgnr, kern)
                    write_output(cusip_heel)
                else:
                    write_output('Incorrect code: ' + code)
            logger.debug(f'Finished converting codes. Thank you for using this program')
            exit_program()
        elif choice == 'q':
            logger.debug(f'Thank you for using this program')
            exit_program()
        else:
            logger.debug(f'Wrong choice. Please try again.')
if __name__ == "__main__":
    main()