import json
import os
import time
import shutil
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from core.utility.functions import get_manga_titles, get_manga_information, get_cover_image, get_manga_statistics, \
    get_manga_description, get_manga_relations, get_published_dates, check_publishing_status, \
    convert_to_appendable_json, get_last_mal_id, convert_to_readable_json

MAL_URL = "https://myanimelist.net/manga/"                                  # MyAnimeList url for characters
ANIME_IMAGES_DIR = 'images/manga/'                                          # Cover images Directory
MAIN_DATA_FILE = 'json/manga/MangaDataCharacters-Main.json'                 # Default Main filename

IN_A_ROW = 1500                                                             # Finishing condition for scraper


def get_manga_item_info(page, ID, filename, open_as):
    soup = BeautifulSoup(page.content, 'html.parser')

    # Testing goes here ----------------------------------

    # ----------------------------------------------------

    if page.status_code == 200:

        with open(filename, open_as) as file:

            # get the id
            mal_id = ID

            # get the mal link
            manga_mal_link = MAL_URL + str(ID)

            # create the final item
            item = {
                'manga_mal_id': mal_id,
                'manga_mal_link': manga_mal_link
            }

            # Get the titles and append them to the main Dictionary
            titles = get_manga_titles(soup)
            item.update(titles)

            # Get the information and append them to the main Dictionary
            info = get_manga_information(soup)
            item.update(info)

            # Get the statistics and append them to the main Dictionary
            stats = get_manga_statistics(soup)
            item.update(stats)

            # Get the description and append them to the main Dictionary
            description = get_manga_description(soup)
            item.update(description)

            # Get the relations and append them to the main Dictionary
            relations = get_manga_relations(soup)
            if relations is None:
                item['relations'] = None
            else:
                item.update(relations)

            # Get the airing status of the anime
            item['publishing'] = check_publishing_status(item['manga_status'])

            # Get aired dates
            dates = get_published_dates(item['manga_published_string'])
            item['dates'] = dates

            # Get the url for the cover image create a name for the image file and download it in the images folder
            if info['manga_image_src'] is not None:
                url = info['manga_image_src']
                name = ANIME_IMAGES_DIR + str(mal_id) + url[-4:]
                get_cover_image(url=url, name=name)

            # check to see if the file ends with a "}" to add a ","
            with open(filename, 'rb+') as end:
                try:
                    end.seek(-1, os.SEEK_END)
                    last_char = end.read().decode('utf-8')
                    if last_char == '}':
                        file.write(', ')
                except OSError:
                    pass

            # write the final item to the json file as json string
            file.write(json.dumps(item) + ',')

            # print the added anime's title and its ID
            print('ID: ' + str(ID) + ' ' + str(datetime.now()) + ' "' + item['manga_title'] + '" has been added. ')
    else:
        if page.status_code == 429:
            print('Too many requests, waiting 3s...')
            time.sleep(3)
        else:
            if page.status_code == 404:
                print('ID ' + str(ID) + " is 404")
            else:
                print('Status code: ' + str(page.status_code))


def scrape_manga_to_file(Type):

    if Type == 'Continue':
        filename = MAIN_DATA_FILE

        shutil.copyfile(MAIN_DATA_FILE, (MAIN_DATA_FILE[:-4] + str(datetime.now()) + '-BACKUP.json').replace(":", "-"))

        last_ID = get_last_mal_id(location=MAIN_DATA_FILE, content='Manga')

        convert_to_appendable_json(MAIN_DATA_FILE)

        # Continue to scrape from the last ID + 1 until it hits the threshold of empty pages in a row
        empty = 0
        x = last_ID + 1
        while True:
            # Try to get the page's content (HTML), if there is a connection error wait 5 seconds then try again

            while True:
                try:
                    page = requests.get(MAL_URL + str(x), headers={'User-agent': 'Mr.163211'})
                    break
                except requests.ConnectionError:
                    print('<-Connection Error-> reconnecting...')
                    time.sleep(5)

            get_manga_item_info(page=page, ID=x, filename=filename, open_as='a')

            # Check how many pages were empty in a row, if >= 300 break
            if page.status_code == 404:
                print(str(empty) + ' empty pages in a row.')
                empty += 1
                if empty >= IN_A_ROW - 1400:
                    break
            else:
                empty = 0
            x += 1

    if Type == 'Initial':
        filename = MAIN_DATA_FILE

        # Check if the file already exists, if it does rename it to Old, and create a new file
        exists = os.path.isfile(filename)
        if exists:
            # Check if -Old.json already exists, if it does generate an unique name for the filename
            old_exists = os.path.isfile('json/manga/MangaDataCharacters-Old.json')
            old = '-Old'
            number = 0
            while old_exists:
                number += 1
                old_filename = 'json/manga/MangaDataCharacters-Old' + str(number) + '.json'
                old_exists = os.path.isfile(old_filename)
                old = '-Old' + str(number)

            os.rename(filename, filename.replace('-Main', old))

        # Start the writing
        with open(filename, 'w') as file:
            file.write('{"data":[')

        # Start to scrape from 0 until it hits the threshold of empty pages in a row
        empty = 0
        x = 1
        while True:
            # Try to get the page's content (HTML), if there is a connection error wait 5 seconds then try again
            while True:
                try:
                    page = requests.get(MAL_URL + str(x), headers={'User-agent': 'Mr.163211'})
                    break
                except requests.ConnectionError:
                    print('<-Connection Error-> reconnecting...')
                    time.sleep(5)

            get_manga_item_info(page=page, ID=x, filename=filename, open_as='a')

            # Check how many pages were empty in a row, if its above the threshold, break
            if page.status_code == 404:
                print(str(empty) + ' empty pages in a row.')
                empty += 1
                if empty >= IN_A_ROW + 1000:
                    break
            else:
                empty = 0
            x += 1

    # Type Update is scraping the already scraped anime to update their values
    if Type == 'Update':
        filename = 'json/manga/MangaDataCharacters-Main-Updated.json'
        last_anime_mal_id = 0

        # Check if there is already an update file in progress
        # If there is, then get the last mal ID
        if os.path.isfile(filename):
            convert_to_readable_json(filename)

            with open(filename, 'r') as file:
                data = json.load(file)

                last_anime_mal_id = data['data'][-1]['manga_mal_id']

            convert_to_appendable_json(filename)

        # If there isn't already an Update file create a new one
        else:
            with open(filename, 'w') as file:
                file.write('{"data":[')

        # Open the main scrape file to get all the anime
        convert_to_readable_json(MAIN_DATA_FILE)
        with open(MAIN_DATA_FILE, 'r') as file:
            data = json.load(file)
        total = len(data['data'])

        # Start scraping from the known indexes
        count = 0
        empty = 0
        for manga in data['data']:
            if manga['manga_mal_id'] <= last_anime_mal_id:
                count += 1
                continue

            # Try to get the page's content (HTML), if there is a connection error wait 5 seconds then try again
            while True:
                try:
                    page = requests.get(MAL_URL + str(manga['manga_mal_id']), headers={'User-agent': 'Mr.163211'})
                    break
                except requests.ConnectionError:
                    print('<-Connection Error-> reconnecting...')
                    time.sleep(5)

            get_manga_item_info(page=page, ID=int(manga['manga_mal_id']), filename=filename, open_as='a')

            # Check how many pages were empty in a row, if >= 300 break
            if page.status_code == 404:
                empty += 1
            count += 1

            print('Complete: ' + '{0:.2f}'.format((count / total) * 100) + '%')

        convert_to_readable_json(filename)

        # If there is already a Latest file, rename it to the current date
        latest_filename = 'json/manga/MangaDataCharacters-Main-Updated-Latest.json'
        if os.path.isfile(latest_filename):
            os.rename(latest_filename, latest_filename.replace('-Latest', '-' + str(datetime.now().date())))

        # Save the Latest update file
        os.rename(filename, filename.replace('-Updated', '-Updated-Latest'))

        # Print the removed manga (REDUNDANT)
        print('Removed manga: ' + str(empty))
