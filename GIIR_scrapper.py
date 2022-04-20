# IMPORT DEPENDENCIES
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
from pprint import PrettyPrinter
import sys

def scrape_data(lower=None, upper=None):
    # SCRAPE DATA
    browser = webdriver.Chrome()
    browser.get('https://www.giiresearch.com/material_report.shtml')

    # data columns
    data = dict()
    data['Published_Date'] = []
    data['Category'] = []
    data['Report_Title'] = []
    data['Summary'] = []
    data['No_of_Pages'] = []
    data['Table_of_Contents'] = []
    data['List_of_Tables'] = []


    # get link to each record on search page
    links = []
    tables = browser.find_elements(by=By.CLASS_NAME, value='plist_item')

    for table in tables:
        links.append(table
                     .find_element(By.CLASS_NAME, 'plist_title')
                     .find_element(By.CLASS_NAME, 'plist_t_box')
                     .find_element(By.CLASS_NAME, 'list_title')
                     .find_element(By.TAG_NAME, 'a')
                     .get_attribute('href')
                    )

    # get record data from each page
    for link in links:
        browser.get(link)
         # to handle unfound pages
        try:
            not_found = (browser.find_element(By.CSS_SELECTOR, '#Body_Wide > table > tbody > tr > td > h1')
                         .find_element(By.TAG_NAME, 'span').text
                        )
            data['Published_Date'].append(np.NaN)
            data['Report_Title'].append(link)
            data['Category'].append(not_found)
            data['Summary'].append(not_found)
            data['No_of_Pages'].append(not_found)
            data['Table_of_Contents'].append(not_found)
            data['List_of_Tables'].append(not_found)
            continue
        except exceptions.NoSuchElementException:
            # date
            date = (browser
                    .find_element(By.CSS_SELECTOR, '#Content_Body > div.prodinfo_body > div.prod_info_box > nobr:nth-child(1) > span > time')
                    .text)
            data['Published_Date'].append(date)

            # title
            title = (browser
                     .find_element(By.CSS_SELECTOR, '#Content_Body > div.prodinfo_body > table > tbody > tr > td.prdinfo_title > h1 > span')
                     .text
            )
            data['Report_Title'].append(title)

            # industry
            industry = browser.find_element(By.CSS_SELECTOR, '#Body_Bread > div > a:nth-child(3)').text
            data['Category'].append(industry)

            # summary 
            summary = browser.find_element(By.CSS_SELECTOR, '#INTRODUCTION > div.cntSecContent').text
            data['Summary'].append(summary)

            # No of pages
            try:
                p_nos =(int(browser.find_element(By.CSS_SELECTOR, '#Content_Body > div.prodinfo_body > div.prod_info_box > nobr:nth-child(5) > span')
                        .text.split(' ')[0]))
            except ValueError:
                p_nos = np.NaN
            except exceptions.NoSuchElementException:
                p_nos = np.NaN
            data['No_of_Pages'].append(p_nos)
            # Table of contents
            try:
                browser.find_element(By.ID, 'Tab').find_elements(By.TAG_NAME, 'li')[1].click()
                t_o_c = browser.find_element(By.ID, 'TOC').text
            except:
                t_o_c=np.NaN
            data['Table_of_Contents'].append(t_o_c)

            # List of Tables
            try:
                browser.find_element(By.ID, 'Tab').find_elements(By.TAG_NAME, 'li')[2].click()
                l_o_t = browser.find_element(By.ID, 'LOT').text
            except:
                l_o_t=np.NaN
            data['List_of_Tables'].append(l_o_t)
    browser.close()

    # CONVERT TO DATAFRAME
    df = pd.DataFrame(data)
    df.to_csv('GIIR_records_unfiltered.csv', index=False)
    df.Published_Date = pd.to_datetime(df.Published_Date) # convert date to date time

    # FILTER TABLE BASED ON GIVEN DATE
    if high and low: # check for date range arguements
        df = df[df.Published_Date[(df.Published_Date >= low)] <= high] # filter 
    elif low: 
        df = df[(df.Published_Date >= low)] # filter

    # convert date obj to str again
    df.Published_Date = df.Published_Date.dt.strftime('%B %d %Y')
    # SAVE TABLE AS CSV FILE
    df.to_csv('GIIR_records_filtered.csv', index=False)
    
    
if '__main__' == __name__:
    while True:
        print('Enter dates below | Enter q to quit')
        low = input('\tLow e.g. January 1, 2022: ')
        high = input('\tHigh e.g. January 1, 2022: ')
        if low == '' and high == '':
            low, high = (None, None)
            break
        elif low == 'q' or high == 'q':
            break
        else:
            try:
                low = pd.to_datetime(low) 
                high = pd.to_datetime(high)
                break
            except:
                print('Enter a correct date format')
                continue
    scrape_data(low, high)
    print('GIIR csv file saved!')
    sys.exit()