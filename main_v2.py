import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
from tqdm.auto import tqdm
import numpy as np

'''
Author: Aru Singh Raghuvanshi

This script scraps data from User Cars section of the main page of OLX.
Can take upto 4 seconds to open each page on the browser,
and a progressbar will indicate the progress of extraction.

Date: 09-10-2021

'''

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/56.0.2924.76 Safari/537.36'}

BASEURL = 'https://www.olx.in'

DRIVER = webdriver.Firefox()

DRIVER.get(BASEURL + '/cars_c84')

NUM_PAGES = 1


def get_carlinks_by_page(NUM_PAGES, DRIVER, BASEURL, HEADERS):
    print('Opening Pages on Browser for Extraction. \033[1;31mPlease Wait...\033[0m')

    def find_fetch_car_links(BASEURL, HEADERS):

        r = requests.get(BASEURL + '/cars_c84', headers=HEADERS)
        sp = BeautifulSoup(r.content, 'lxml')

        carlinks = []

        carlist = sp.find_all('li', class_='EIR5N')

        for item in carlist:
            for link in item.find_all('a', href=True):
                carlinks.append(BASEURL + link['href'])

        print(f'Total links found on page: {len(carlinks)}')
        time.sleep(1)
        return carlinks

    cl, clx, count = [], [], 1

    while count <= NUM_PAGES:

        print(f'\nLoading Page: \033[0;34m{count} of {NUM_PAGES}\033[0m.')
        try:
            btn = DRIVER.find_element_by_class_name('JbJAl')
        except Exception as e:
            print(f'Element not found on Page - {e}')

        time.sleep(1.5)
        try:
            btn.click()
        except Exception as e:
            print(f'Element not found on page for extraction - {e}')

        count += 1
        k = find_fetch_car_links(BASEURL, HEADERS)
        cl.append(k)

    for ele in range(0, len(cl)):
        clx = clx + cl[ele]

    print(f'\nTotal Records Fetched: {len(clx)} from {NUM_PAGES} pages.')
    return clx


def clean_up_string(original_string):
    characters_to_remove = "!()#~`$₹@[]"

    new_string = original_string
    for character in characters_to_remove:
        new_string = new_string.replace(character, "")

    return new_string.strip()


def get_vehicle_data(link):
    vdata = {}

    r = requests.get(link, headers=HEADERS)
    sp = BeautifulSoup(r.content, 'lxml')

    try:
        name = sp.find('div', class_='_35xN1').text.strip()
        name = clean_up_string(name)
        vdata['name'] = name
    except Exception as e:
        name = np.NaN
        vdata['name'] = name
        print(f'Data not found - {e}')

    try:
        price = sp.find('div', class_='_3FkyT').text.strip()
        price = clean_up_string(price)
        vdata['price'] = price
    except Exception as e:
        price = 'Not Listed'
        vdata['price'] = price
        print(f'Data not found - {e}')

    #     try:
    #         mileage = sp.find('div', class_='_3qDp0').text.strip()
    #         mileage = clean_up_string(mileage)
    #         vdata['mileage'] = mileage
    #     except Exception as e:
    #         mileage = 'Not Listed'
    #         vdata['mileage'] = mileage
    #         print(f'Data not found - {e}')

    try:
        sold_by = sp.find('span', class_='_1hYGL').text.strip()
        sold_by = clean_up_string(sold_by)
        vdata['sold_by'] = sold_by
    except Exception as e:
        sold_by = 'Unknown'
        vdata['sold_by'] = sold_by
        print(f'Data not found - {e}')

    try:
        details = ''.join(str(sp.find_all('div', class_='_1gasz')))
        details = clean_up_string(details)
        details = ' '.join(BeautifulSoup(details, "html.parser").stripped_strings)
        details = details.split(',')

        vdata['owner'] = details[0].strip()
        vdata['location'] = details[1].strip()
        vdata['city'] = details[2].strip()
        vdata['posting_date'] = details[3].strip()
    except Exception as e:
        details = 'Not found'
        vdata['owner'] = 'Unknown'
        vdata['location'] = 'Unknown'
        vdata['city'] = 'N/A'
        vdata['posting_date'] = 'Not Listed'
        print(f'Data not found - {e}')

    try:
        details2 = ''.join(str(sp.find_all('div', class_='_3qDp0')))
        details2 = clean_up_string(details2)
        details2 = ' '.join(BeautifulSoup(details2, "html.parser").stripped_strings)

        if details2.count(',') > 2:
            details2 = details2.split(',')
            details2[1:3] = [''.join(details2[1:3])]
        else:
            details2 = details2.split(',')

        vdata['fuel'] = details2[0].strip()
        vdata['mileage'] = details2[1].strip()
        vdata['transmission'] = details2[2].strip()
    except Exception as e:
        vdata['fuel'] = 'Unknown'
        vdata['mileage'] = 'N/A'
        vdata['transmission'] = 'N/A'
        print(f'Data not found - {e}')

    try:
        desc = ''.join(str(sp.find_all('div', class_='_2e_o8')))
        desc = ' '.join(BeautifulSoup(desc, "html.parser").stripped_strings)
        desc = clean_up_string(desc)
        vdata['desc'] = desc
    except Exception as e:
        desc = 'N/A'
        vdata['desc'] = desc
        print(f'Data not found - {e}')

    return vdata


# -------------- Extraction and Inference Pipeline ----------------- ]

carlinks = get_carlinks_by_page(NUM_PAGES, DRIVER, BASEURL, HEADERS)

vehicle_data = []
color = 'dodgerblue'

print('\n\033[0;32mDone.\033[0m')
print('\n\033[0;32mExtracting Data...\033[0m')

for x in tqdm(carlinks, desc='PROGRESS', colour=color, unit='record'):
    vh = get_vehicle_data(x)
    vehicle_data.append(vh)

print('\033[0;32mDone.\033[0m')

df = pd.DataFrame(vehicle_data)
df.dropna(how='any', axis=0, inplace=True)
df.to_csv(f'OLX_used_cars_{NUM_PAGES}p.csv', index=False)
