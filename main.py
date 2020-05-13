import schedule
import time

import anime_scraper
import character_scraper
import manga_scraper
from core.utility.functions import convert_to_appendable_json, convert_to_readable_json

# IN_A_ROW = 1000  # Finishing condition for scraper


version_name = 'MAL Scraper v2.0'
content = None

# Simple User Interface
while True:
    print('\nWelcome to ' + version_name + ',\nType Help for commands')
    if content:
        print('Content selected: ' + str(content))
    else:
        print('Content selected: None')
    user_input = input('Command: ')

    # HELP
    if user_input == 'Help':
        print('Command: "Initial". The initial scan starts scraping from the very start, from index 0 until it reaches '
              '200 continues empty(404 error) pages.')
        print('Command: "Continue". Continues from the last scraped index until it reaches 200 continues empty(404 '
              'error) pages.')
        print('Command "Missing". Starts scraping for missing anime, ignoring the already added indexes until the last '
              'added index.')
        print('Command "Readable". Converts the Main Anime file into a properly formatted json file.')
        print('Command "Appendable". Converts the Main Anime file into an appendable version of the file for the '
              'scraper to be able to continue.')
        print('Command "Exit". Exits the scraper.')

    # SELECT CONTENT ANIME
    elif user_input == 'Anime':
        print('Content ANIME selected.')
        content = 'Anime'

    # SELECT CONTENT CHARACTERS
    elif user_input == 'Characters':
        print('Content CHARACTERS selected.')
        content = 'Characters'

    # SELECT CONTENT MANGA
    elif user_input == 'Manga':
        print('Content MANGA selected.')
        content = 'Manga'

    # INITIAL SCAN
    elif user_input == 'Initial':
        if content == 'Anime':
            print('Command "Initial" acknowledged, ' + version_name + ' starting initial scrape for ANIME from index '
                                                                      '0.')
            anime_scraper.scrape_to_file(Type='Initial')
        elif content == 'Characters':
            print('Command "Initial" acknowledged, ' + version_name + ' starting initial scrape for CHARACTERS from '
                                                                      'index 0.')
            character_scraper.scrape_characters_to_file(Type='Initial')
        elif content == 'Manga':
            print('Command "Initial" acknowledged, ' + version_name + ' starting initial scrape for MANGA from index '
                                                                      '0.')
            manga_scraper.scrape_manga_to_file(Type='Initial')

        else:
            print('Error! No content selected!')

    # MISSING SCAN
    elif user_input == 'Missing':
        print('Command "Missing" acknowledged, ' + version_name + ' looking for missing anime.')
        # anime_scraper.scrape_to_file(Type='Missing')

    # CONTINUATION SCAN
    elif user_input == 'Continue':
        if content == 'Anime':
            print('Command "Continue" acknowledged, ' + version_name + ' continuing scraping for ANIME from last '
                                                                       'index.')
            anime_scraper.scrape_to_file(Type='Continue')
        elif content == 'Characters':
            print('Command "Continue" acknowledged, ' + version_name + ' continuing scraping for CHARACTERS from last '
                                                                       'index.')
            character_scraper.scrape_characters_to_file(Type='Continue')
        elif content == 'Manga':
            print('Command "Continue" acknowledged, ' + version_name + ' continuing scraping scrape for MANGA from last'
                                                                       ' index.')
            manga_scraper.scrape_manga_to_file(Type='Continue')

        else:
            print('Error! No content selected!')

    # UPDATE SCAN
    elif user_input == 'Update':
        if content == 'Anime':
            print('Command "Continue" acknowledged, ' + version_name + ' continuing scraping for ANIME from last '
                                                                       'index.')
            anime_scraper.scrape_to_file(Type='Update')
        elif content == 'Characters':
            print('There is no need to update Characters.')
        elif content == 'Manga':
            print('Command "Continue" acknowledged, ' + version_name + ' continuing scraping scrape for MANGA from last'
                                                                       ' index.')
            manga_scraper.scrape_manga_to_file(Type='Update')

        else:
            print('Error! No content selected!')

    # START AUTOMATIC UPDATE
    elif user_input == 'Automatic':
        print('Update schedule:\n01:00 - Anime\n02:00 - Manga\n03:00 - Characters\nSundays: 00:00 - Update Anime')

        schedule.every().day.at("01:00").do(anime_scraper.scrape_to_file, 'Continue')
        schedule.every().day.at("02:00").do(manga_scraper.scrape_manga_to_file, 'Continue')
        schedule.every().day.at("03:00").do(character_scraper.scrape_characters_to_file, 'Continue')

        schedule.every().sunday.at("00:00").do(anime_scraper.scrape_to_file, 'Update')

        while True:
            schedule.run_pending()
            time.sleep(60)  # wait one minute

    # CONVERT MAIN JSON TO READABLE
    elif user_input == 'Readable':
        print('Command: "Readable" acknowledged, converting ' + anime_scraper.MAIN_DATA_FILE +
              ' to readable json.')
        convert_to_readable_json(anime_scraper.MAIN_DATA_FILE)

    # CONVERT MAIN JSON TO APPENDABLE
    elif user_input == 'Appendable':
        print('Command: "Appendable" acknowledged, converting ' + anime_scraper.MAIN_DATA_FILE +
              ' to appendable json.')
        convert_to_appendable_json(anime_scraper.MAIN_DATA_FILE)

    # EXIT THE PROGRAM
    elif user_input == 'Exit':
        print('Goodbye!')
        break

    # Invalid command
    else:
        print('Unknown command: "' + user_input + '" Type "Help for list of commands."')

    # print('Command: ' + user_input)
