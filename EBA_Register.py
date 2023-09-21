# This script is intended to process Payment Institutions Register data
# from the European Banking Association
# It is based on downloaded json files from the website
# https://euclid.eba.europa.eu/register/pir/disclaimer
#
# Mark Bruyneel
# 2023-09-14
# Script version 1.1

import os
import pandas as pd
import numpy as np
import json
from csv import reader
from loguru import logger
import time
from datetime import datetime, timedelta
from pathlib import Path

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

logger.add(r'U:\Werk\Data Management\Python\\Files\output\EBA_Process_'+runday+'.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")
@logger.catch()

def main():
    # Step 1 Read Json files
    # Establish location and files with data. Put the filenames in a table
    # and add the date in the file name as data for a column
    pathi = input('Provide folder and the name of the Json file.\n First provide the folder name. Example folder name: c:\\temp\ \n')
    filename = input('\nNow provide the Json filename.\n')
    namefile = pathi + filename
    logger.debug(f'Folder & Json file name provided: ' + namefile)

    # Step 2 Generate folder for the output data
    Path(pathi + 'output').mkdir(parents=True, exist_ok=True)

    # Step 3 Create ean empty data frame for the Payment entities
    PIR_entities = pd.DataFrame()

    # This step is necessary as the download usually is a list with as
    # the first item a copyright notice (etc.) and the data is in the second (list) item.
    f = open(f''+namefile, 'rb')
    data = json.load(f)
    datatwo = data[1]

    # Iterating through the json list to get specific items
    # First put them in item lists and then create a table by combining them
    # The EBA register has multilevels and requires separate parts to be processed
    # separately. At a later stage these tables (csv) can be combined if needed.

    # Step 4 EBA Register base level part (1).
    id_list = []
    entitycode = []
    entitytype = []
    eba_entity_version = []
    for l1 in datatwo:
        logger.debug('Processing EBA entity main data: ' + l1['EntityCode'])
        id_list.append(l1['CA_OwnerID'])
        entitycode.append(l1['EntityCode'])
        entitytype.append(l1['EntityType'])
        eba_entity_version.append(l1['__EBA_EntityVersion'])
    id_data = {'ID': id_list}
    test_list = pd.DataFrame(id_data)
    test_list['EntityCode'] = entitycode
    test_list['EntityType'] = entitytype
    test_list['EBA_Entity_Version'] = eba_entity_version
    PIR_entities = pd.concat([PIR_entities, test_list], ignore_index=True)

    # Export part 1 result as a CSV file with the date of the Python run
    PIR_entities.to_csv(f''+pathi+'output\EBA_PIR_list_1_Entities_'+runday+'.csv', encoding='utf-8')

    # Step 5 Get the properties from the EBA Register for each entity.
    # This level has National property level data as reported by nations's main authority.
    # First create a number of lists based on the maximum nr. of expected properties (14)
    # Create a DataFrame / table for the properties
    Prop_Entities = pd.DataFrame()

    # Convert list of entity properties (list of dictionaries) to Dataframe/table
    # This DataFrame / table will have separate rows for each characteristic and one cell
    # that actually has the property data.
    for l1 in datatwo:
        logger.debug('Processing EBA entity properties: ' + l1['EntityCode'])
        props = pd.DataFrame.from_records(l1['Properties'])
        props['EntityCode'] = l1['EntityCode']
        Prop_Entities = pd.concat([Prop_Entities, props], ignore_index=True)

    # Use the generated Dataframe to split & clean and merge the data as it is
    # inefficient due to empty cells as each property gets it's own row
    # The dataframe should have 14 columns with column 8 being: EBA_EntityVersion
    # Fields: ENT_AUT, ENT_NAT_REF_COD, ENT_NAM, ENT_ADD, ENT_TOW_CIT_RES, ENT_POS_COD,
    # ENT_COU_RES, EBA_Entity_Version, ENT_NAM_COM, ENT_EXC, ENT_DES_ACT_EXC_SCP,
    # ENT_TYP_PAR_ENT, ENT_COD_PAR_ENT, DER_CHI_ENT_AUT
    #
    # WARNING: The number of fields may depend on the size of the download as this depends
    # on what data is included in the Json File! I have based it on the full register
    # download file. First make subsets for each property and remove cells with no data.
    Prop1 = Prop_Entities.iloc[:, [0, 7]].copy()
    Prop1.dropna(subset=['ENT_AUT'], inplace=True)
    # List type ENT-AUT needs to be converted str for the merge to succeed
    Prop1['ENT_AUT'] = Prop1["ENT_AUT"].map(str)

    Prop2 = Prop_Entities.iloc[:, [1, 7]].copy()
    Prop2.dropna(subset=['ENT_NAT_REF_COD'], inplace=True)
    Prop3 = Prop_Entities.iloc[:, [2, 7]].copy()
    Prop3.dropna(subset=['ENT_NAM'], inplace=True)
    Prop4 = Prop_Entities.iloc[:, [3, 7]].copy()
    Prop4.dropna(subset=['ENT_ADD'], inplace=True)
    Prop5 = Prop_Entities.iloc[:, [4, 7]].copy()
    Prop5.dropna(subset=['ENT_TOW_CIT_RES'], inplace=True)
    Prop6 = Prop_Entities.iloc[:, [5, 7]].copy()
    Prop6.dropna(subset=['ENT_POS_COD'], inplace=True)
    Prop7 = Prop_Entities.iloc[:, [6, 7]].copy()
    Prop7.dropna(subset=['ENT_COU_RES'], inplace=True)
    Prop8 = Prop_Entities.iloc[:, [7, 8]].copy()
    Prop8.dropna(subset=['ENT_NAM_COM'], inplace=True)
    Prop9 = Prop_Entities.iloc[:, [7, 9]].copy()
    Prop9.dropna(subset=['ENT_EXC'], inplace=True)
    Prop10 = Prop_Entities.iloc[:, [7, 10]].copy()
    Prop10.dropna(subset=['ENT_DES_ACT_EXC_SCP'], inplace=True)
    Prop11 = Prop_Entities.iloc[:, [7, 11]].copy()
    Prop11.dropna(subset=['ENT_TYP_PAR_ENT'], inplace=True)
    Prop12 = Prop_Entities.iloc[:, [7, 12]].copy()
    Prop12.dropna(subset=['ENT_COD_PAR_ENT'], inplace=True)
    Prop13 = Prop_Entities.iloc[:, [7, 13]].copy()
    Prop13.dropna(subset=['DER_CHI_ENT_AUT'], inplace=True)

    # Now merge the subsets into a new table/Dataframe
    Merge1 = pd.merge(Prop1, Prop2, on=['EntityCode'], how='outer')
    Merge1.drop_duplicates(subset=['ENT_AUT', 'EntityCode', 'ENT_NAT_REF_COD'], keep='first', ignore_index=True, inplace=True)
    Merge2 = pd.merge(Prop3, Merge1, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge2 = Merge2.applymap(str)
    Merge2.drop_duplicates(subset=['ENT_AUT', 'EntityCode', 'ENT_NAT_REF_COD', 'ENT_NAM'], keep='first', ignore_index=True, inplace=True)
    Merge3 = pd.merge(Prop4, Merge2, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge3 = Merge3.applymap(str)
    Merge3.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge4 = pd.merge(Prop5, Merge3, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge4 = Merge4.applymap(str)
    Merge4.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge5 = pd.merge(Prop6, Merge4, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge5 = Merge5.applymap(str)
    Merge5.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge6 = pd.merge(Prop7, Merge5, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge6 = Merge6.applymap(str)
    Merge6.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge7 = pd.merge(Prop8, Merge6, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge7 = Merge7.applymap(str)
    Merge7.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge8 = pd.merge(Prop9, Merge7, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge8 = Merge8.applymap(str)
    Merge8.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge9 = pd.merge(Prop10, Merge8, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge9 = Merge9.applymap(str)
    Merge9.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge10 = pd.merge(Prop11, Merge9, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge10 = Merge10.applymap(str)
    Merge10.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge11 = pd.merge(Prop12, Merge10, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge11 = Merge11.applymap(str)
    Merge11.drop_duplicates(keep='first', ignore_index=True, inplace=True)
    Merge12 = pd.merge(Prop13, Merge11, on=['EntityCode'], how='outer')
    # To avoid problems with columns that keep being interpreted as lists:
    Merge12 = Merge12.applymap(str)
    Merge12.drop_duplicates(keep='first', ignore_index=True, inplace=True)

    # Order the fields as they were in the original Json download file
    Merge12 = Merge12[['ENT_AUT', 'ENT_NAT_REF_COD', 'ENT_NAM', 'ENT_ADD', 'ENT_TOW_CIT_RES', 'ENT_POS_COD', 'ENT_COU_RES',	'EntityCode', 'ENT_NAM_COM', 'ENT_EXC', 'ENT_DES_ACT_EXC_SCP', 'ENT_TYP_PAR_ENT', 'ENT_COD_PAR_ENT', 'DER_CHI_ENT_AUT']]
    # Download the properties as a separate table
    Merge12.to_csv(f'' + pathi + 'output\EBA_PIR_list_2_EntityProperties_' + runday + '.csv', encoding='utf-8')

    # Step 6 Get the services for each entity in the register. These will only
    # be there for active entities (according to the information at the time of
    # the download. Country Codes are 2 digit ISO 3166 international standard codes.
    # For an overview see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #
    # The services are based on Annex I to PSD2 and issuing electronic money under EMD2.
    # See also: https://en.wikipedia.org/wiki/Payment_Services_Directive
    # And: https://en.wikipedia.org/wiki/E-Money_Directive
    #
    Serv_Entities = pd.DataFrame()
    entitycode_s = []
    entity_sco = []
    entity_sty = []
    for l1 in datatwo:
        entity_length = len(l1)
        if entity_length < 6:
            pass
        else:
            servlist = l1['Services']
            logger.debug('Processing EBA entity services')
            for dataitem in servlist:
                for country in dataitem:
                    service_codes = dataitem[country]
                    entitycode_s.extend([l1['EntityCode']]*len(service_codes))
                    entity_sco.extend([country]*len(service_codes))
                    entity_sty.extend(service_codes)
    # Result for each service by nation should be a row of three items:
    # Entity Code, CountryCode, ServiceCode
    id_data_s = {'EntityCode': entitycode_s}
    test_lists = pd.DataFrame(id_data_s)
    test_lists['EntityCountryServCode'] = entity_sco
    test_lists['EntityServType'] = entity_sty
    Serv_Entities = pd.concat([Serv_Entities, test_lists], ignore_index=True)
    Serv_Entities.to_csv(f'' + pathi + 'output\EBA_PIR_list_3_EntityServices_' + runday + '.csv', encoding='utf-8')

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
