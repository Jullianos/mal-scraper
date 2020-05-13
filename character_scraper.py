import json
import os
import time
import shutil
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from core.utility.functions import convert_to_appendable_json, get_cover_image, get_last_mal_id, get_character_name, \
    get_character_info, get_character_description, get_character_voice_actors, get_character_roles

MAL_URL = "https://myanimelist.net/character/"                      # MyAnimeList url for characters
CHARACTERS_IMAGES_DIR = 'images/characters/'                        # Cover images Directory
MAIN_DATA_FILE = 'json/characters/AnimeDataCharacters-Main.json'    # Default Main filename

IN_A_ROW = 500                                                      # Finishing condition for scraper


def get_character_item_info(page, ID, filename, open_as):
    soup = BeautifulSoup(page.content, 'html.parser')

    # Check if the page is 404
    exists = soup.find('div', {'class': 'badresult'})

    if exists:
        print('ID: ' + str(ID) + " is 404")
        return 404

    # Testing goes here ----------------------------------

    # ----------------------------------------------------

    if page.status_code == 200:

        with open(filename, open_as) as file:

            # get the id
            mal_id = ID

            # get the mal link
            character_mal_link = MAL_URL + str(ID)

            # create the final item
            item = {
                'character_mal_id': mal_id,
                'character_mal_link': character_mal_link
            }

            # get the name of the characters
            name = get_character_name(soup)
            item['character_name'] = name

            # get the cover image source and
            info = get_character_info(soup)
            item.update(info)

            # get the synopsis of the character
            background = get_character_description(soup)
            item.update(background)

            # get the voice actors of the character
            item['character_voice_actors'] = get_character_voice_actors(soup)

            # get the character roles for Anime

            roles = get_character_roles(soup)

            item['character_anime_roles'] = roles[0]
            item['character_manga_roles'] = roles[1]

            # Get the url for the cover image create a name for the image file and download it in the images folder
            if info['character_image_src'] is not None:
                url = item['character_image_src']
                name = CHARACTERS_IMAGES_DIR + str(mal_id) + url[-4:]
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
            print('ID: ' + str(ID) + ' ' + str(datetime.now()) + ' "' + str(item['character_name']) +
                  '" has been added. ')
    else:
        if page.status_code == 429:
            print('Too many requests, waiting 3s...')
            time.sleep(3)
        else:
            if page.status_code == 404:
                print('ID ' + str(ID) + " is 404")
            else:
                print('Status code: ' + str(page.status_code))


def scrape_characters_to_file(Type):

    if Type == 'Continue':
        filename = MAIN_DATA_FILE

        shutil.copyfile(MAIN_DATA_FILE, (MAIN_DATA_FILE[:-4] + str(datetime.now()) + '-BACKUP.json').replace(":", "-"))

        last_ID = get_last_mal_id(location=MAIN_DATA_FILE, content='Character')

        convert_to_appendable_json(MAIN_DATA_FILE)

        # Continue to scrape from the last ID + 1 until it hits 300 empty pages in a row
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

            status_code = get_character_item_info(page=page, ID=x, filename=filename, open_as='a')

            # Check how many pages were empty in a row, if >= 300 break
            if status_code == 404:
                print(str(empty) + ' empty pages in a row.')
                empty += 1
                if empty >= IN_A_ROW + 500:
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
            old_exists = os.path.isfile('json/characters/AnimeDataCharacters-Old.json')
            old = '-Old'
            number = 0
            while old_exists:
                number += 1
                old_filename = 'json/characters/AnimeDataCharacters-Old' + str(number) + '.json'
                old_exists = os.path.isfile(old_filename)
                old = '-Old' + str(number)

            os.rename(filename, filename.replace('-Main', old))

        # Start the writing
        with open(filename, 'w') as file:
            file.write('{"data":[')

        # Start to scrape from 0 until it hits 300 empty pages in a row
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

            get_character_item_info(page=page, ID=x, filename=filename, open_as='a')

            # Check how many pages were empty in a row, if >= 300 break
            if page.status_code == 404:
                print(str(empty) + ' empty pages in a row.')
                empty += 1
                if empty >= 2500:
                    break
            else:
                empty = 0
            x += 1
