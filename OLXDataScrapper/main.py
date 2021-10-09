import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
from tqdm import tqdm

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/56.0.2924.76 Safari/537.36'}

BASEURL = 'https://www.olx.in'

DRIVER = webdriver.Firefox()

DRIVER.get(BASEURL + '/cars_c84')

NUM_PAGES = 3


def get_carlinks_by_page(NUM_PAGES, DRIVER, BASEURL, HEADERS):
    def find_fetch_car_links(BASEURL, HEADERS):

        r = requests.get(BASEURL + '/cars_c84', headers=HEADERS)
        sp = BeautifulSoup(r.content, 'lxml')

        carlinks = []

        carlist = sp.find_all('li', class_='EIR5N')

        for item in carlist:
            for link in item.find_all('a', href=True):
                carlinks.append(BASEURL + link['href'])

        print(f'Total links found on page: {len(carlinks)}')
        return carlinks

    cl, clx = [], []
    count = 1
    while count <= NUM_PAGES:
        time.sleep(0.5)
        btn = DRIVER.find_element_by_class_name('JbJAl')
        print(f'\nLoading Page: {count} of {NUM_PAGES}.')
        time.sleep(2)
        btn.click()
        count += 1
        k = find_fetch_car_links(BASEURL, HEADERS)
        cl.append(k)

    for ele in range(0, len(cl)):
        clx = clx + cl[ele]

    print(f'\nTotal Records Fetched: {len(clx)} from {NUM_PAGES} pages.')
    return clx


carlinks = get_carlinks_by_page(NUM_PAGES, DRIVER, BASEURL, HEADERS)


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
        name = 'Unnamed'
        vdata['name'] = name
        print(f'Data not found - {e}')

    try:
        fueltype = sp.find('div', class_='_3qDp0').text.strip()
        fueltype = clean_up_string(fueltype)
        vdata['fueltype'] = fueltype
    except Exception as e:
        fueltype = 'Unknown'
        vdata['fueltype'] = fueltype
        print(f'Data not found - {e}')

    try:
        price = sp.find('div', class_='_3FkyT').text.strip()
        price = clean_up_string(price)
        vdata['price'] = price
    except Exception as e:
        price = 'Not Listed'
        vdata['price'] = price
        print(f'Data not found - {e}')

    try:
        sold_by = sp.find('span', class_='_1hYGL').text.strip()
        sold_by = clean_up_string(sold_by)
        vdata['sold_by'] = sold_by
    except Exception as e:
        sold_by = 'Unknown'
        vdata['sold_by'] = sold_by
        print(f'Data not found - {e}')

    details = ''.join(str(sp.find_all('div', class_='_1gasz')))
    details = clean_up_string(details)
    details = ' '.join(BeautifulSoup(details, "html.parser").stripped_strings)
    details = details.split(',')
    try:
        vdata['owner'] = details[0].strip()
        vdata['location'] = details[1].strip()
        vdata['city'] = details[2].strip()
        vdata['posting_date'] = details[3].strip()
    except Exception as e:
        details = 'Not found'
        print(f'Data not found - {e}')
        vdata['owner'] = ''
        vdata['location'] = ''
        vdata['city'] = ''
        vdata['posting_date'] = ''

    try:
        desc = ''.join(str(sp.find_all('div', class_='_2e_o8')))
        desc = ' '.join(BeautifulSoup(desc, "html.parser").stripped_strings)
        desc = clean_up_string(desc)
        vdata['desc'] = desc
    except Exception as e:
        desc = 'Not N/A'
        vdata['desc'] = desc
        print(f'Data not found - {e}')

    return vdata


vehicle_data = []
for x in tqdm(carlinks):
    vh = get_vehicle_data(x)
    vehicle_data.append(vh)

df = pd.DataFrame(vehicle_data)

df.to_csv(f'OLX_used_cars_{NUM_PAGES}p.csv', index=False)