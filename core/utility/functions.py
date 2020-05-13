import re
import requests
import time
import json
from datetime import datetime

from .extras import get_duration_mins_from_duration, get_dates, get_manga_dates
import anime_scraper


# ###########################################################################
# ###########################################################################
#
# FUNCTIONS FOR ANIME
#
# ###########################################################################
# ###########################################################################


def get_last_mal_id(location, content):
    convert_to_readable_json(location)
    with open(location, "r") as file:
        parsed = json.load(file)

        if content == 'Anime':

            print('file: ' + location)

            last_mal_id = parsed['data'][0]['anime_mal_id']
            for j in range(len(parsed['data'])):
                mal_id = parsed['data'][j]['anime_mal_id']
                if mal_id > last_mal_id:
                    last_mal_id = mal_id

        elif content == 'Character':

            print('file: ' + location)

            last_mal_id = parsed['data'][0]['character_mal_id']
            for j in range(len(parsed['data'])):
                mal_id = parsed['data'][j]['character_mal_id']
                if mal_id > last_mal_id:
                    last_mal_id = mal_id

        elif content == 'Manga':
            print('file: ' + location)

            last_mal_id = parsed['data'][0]['manga_mal_id']
            for j in range(len(parsed['data'])):
                mal_id = parsed['data'][j]['manga_mal_id']
                if mal_id > last_mal_id:
                    last_mal_id = mal_id

        else:
            print("Cant't find Last ID, wrong content given!")
            return None

        print('Last ID = ' + str(last_mal_id))

    return last_mal_id


def get_titles(soup):
    # get the titles
    try:
        anime_title = soup.h1.span.text
    except AttributeError:
        anime_title = None

    try:
        anime_title_english = soup.find('span', text="English:").parent.text \
            .replace('\n', '') \
            .replace('English: ', '') \
            .strip(' ')
    except AttributeError:
        anime_title_english = None

    try:
        anime_title_japanese = soup.find('span', text="Japanese:").parent.text \
            .replace('\n', '') \
            .replace('Japanese: ', '') \
            .strip(' ')
    except AttributeError:
        anime_title_japanese = None

    try:
        anime_title_synonyms = soup.find('span', text="Synonyms:").parent.text \
            .replace('\n', '') \
            .replace('Synonyms: ', '') \
            .strip(' ')
    except AttributeError:
        anime_title_synonyms = None

    titles = {
        'anime_title': anime_title,
        'anime_title_english': anime_title_english,
        'anime_title_japanese': anime_title_japanese,
        'anime_title_synonyms': anime_title_synonyms
    }

    return titles


def get_information(soup):
    try:
        print(soup.find('img', attrs={'itemprop': 'image'}))
        anime_image_src = soup.find('img', attrs={'itemprop': 'image'})['src']
    except TypeError:
        anime_image_src = None

    anime_type = soup.find('span', text='Type:').parent.text \
        .replace('\n', '') \
        .replace('Type:', '') \
        .replace(' ', '')

    try:
        anime_episodes = int(soup.find('span', text='Episodes:').parent.text
                             .replace('\n', '')
                             .replace('Episodes:', '')
                             .replace(' ', ''))
    except ValueError:
        anime_episodes = None

    anime_status = soup.find('span', text='Status:').parent.text \
        .replace('\n', '') \
        .replace('Status:', '') \
        .strip(' ')

    anime_aired_string = soup.find('span', text='Aired:').parent.text \
        .replace('\n', '') \
        .replace('Aired:', '') \
        .strip(' ')

    try:
        anime_premiered = soup.find('span', text='Premiered:').parent.text \
            .replace('\n', '') \
            .replace('Premiered:', '')
    except AttributeError:
        anime_premiered = None

    try:
        anime_broadcast = soup.find('span', text='Broadcast:').parent.text \
            .replace('\n', '') \
            .replace('Broadcast:', '') \
            .strip(' ')
    except AttributeError:
        anime_broadcast = None

    anime_producers = re.sub(' +', ' ', soup.find('span', text='Producers:').parent.text
                             .replace('\n', '')
                             .replace('Producers:', '')
                             .strip(' '))
    if anime_producers == 'None found, add some':
        anime_producers = None

    anime_licensors = re.sub(' +', ' ', soup.find('span', text='Licensors:').parent.get_text()
                             .replace('\n', '')
                             .replace('Licensors:', '')
                             .strip(' '))
    if anime_licensors == 'None found, add some':
        anime_licensors = None

    anime_studios = re.sub(' +', ' ', soup.find('span', text='Studios:').parent.get_text()
                           .replace('\n', '')
                           .replace('Studios:', '')
                           .strip(' '))
    if anime_studios == 'None found, add some':
        anime_studios = None

    anime_source = soup.find('span', text='Source:').parent.text \
        .replace('\n', '') \
        .replace('Source:', '') \
        .replace(' ', '')

    anime_genres = soup.find('span', text='Genres:').parent.get_text() \
        .replace('\n', '') \
        .replace('Genres:', '')

    anime_duration = soup.find('span', text='Duration:').parent.get_text() \
        .replace('\n', '') \
        .replace('Duration:', '') \
        .strip(' ')

    anime_rating = soup.find('span', text='Rating:').parent.get_text() \
        .replace('\n', '') \
        .replace('Rating:', '') \
        .strip(' ')

    info = {
        'anime_image_src': anime_image_src,
        'anime_type': anime_type,
        'anime_episodes': anime_episodes,
        'anime_status': anime_status,
        'anime_aired_string': anime_aired_string,
        'anime_premiered': anime_premiered,
        'anime_broadcast': anime_broadcast,
        'anime_producers': anime_producers,
        'anime_licensors': anime_licensors,
        'anime_studios': anime_studios,
        'anime_source': anime_source,
        'anime_genres': anime_genres,
        'anime_duration': anime_duration,
        'anime_rating': anime_rating
    }

    return info


def get_statistics(soup):
    try:
        if 'N/A' in str(soup.find('span', attrs={'itemprop': 'ratingValue'})):
            anime_score = None
        else:
            anime_score = float(soup.find('span', attrs={'itemprop': 'ratingValue'}).text)
    except AttributeError:
        try:
            anime_score = float(soup.find('span', text='Score:').next_sibling.next_sibling.text)
        except ValueError:
            anime_score = None
        except AttributeError:
            anime_score = 'Something went wrong again'

    try:
        anime_scored_by = int(soup.find('span', attrs={'itemprop': 'ratingCount'}).text
                              .replace(',', ''))
    except AttributeError:
        try:
            anime_scored_by = int(soup.find('span', text='Score:')
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .text)
        except AttributeError:
            anime_scored_by = 'Something went wrong again'

    remove = soup.find('span', text='Ranked:').parent.find('sup')
    remove.extract()
    remove = soup.find('span', text='Ranked:').parent.find('div')
    remove.extract()

    if "N/A" not in soup.find('span', text='Ranked:').parent.text:
        anime_ranked = int(soup.find('span', text='Ranked:').parent.text
                           .replace('\n', '')
                           .replace('Ranked:', '')
                           .replace(' ', '')
                           .replace('#', ''))
    else:
        anime_ranked = None

    anime_popularity = int(soup.find('span', text='Popularity:').parent.text
                           .replace('\n', '')
                           .replace('Popularity:', ' ')
                           .replace('#', '')
                           .strip(' '))

    anime_members = int(soup.find('span', text='Members:').parent.text
                        .replace('\n', '')
                        .replace('Members:', '')
                        .replace(' ', '')
                        .replace(',', ''))

    anime_favorites = int(soup.find('span', text='Favorites:').parent.text
                          .replace('\n', '')
                          .replace('Favorites:', '')
                          .replace(' ', '')
                          .replace(',', ''))

    stats = {
        'anime_score': anime_score,
        'anime_scored_by': anime_scored_by,
        'anime_ranked': anime_ranked,
        'anime_popularity': anime_popularity,
        'anime_members': anime_members,
        'anime_favorites': anime_favorites,
    }

    return stats


def get_description(soup):
    try:
        anime_synopsis = soup.find('span', attrs={'itemprop': 'description'}).get_text()
    except AttributeError:
        anime_synopsis = None

    try:
        background = soup.find_all('table')[2].find('td').find_all('h2')[1].next_sibling
    except IndexError:
        background = soup.find('h2', attrs={'style': 'margin-top: 15px;'}).next_sibling

    anime_background = ''

    while background.next_sibling is not None:
        if background.name == 'i':
            anime_background += background.text
        else:
            anime_background += str(background)
        if background.next_sibling.name == 'div' or background.next_sibling.name == 'a':
            break
        else:
            background = background.next_sibling
    anime_background = anime_background.replace('<br/>', '').replace('\n', '')

    if anime_background.__contains__('No background information'):
        anime_background = None

    description = {
        'anime_synopsis': anime_synopsis,
        'anime_background': anime_background
    }

    return description


def get_relations(soup):
    try:
        anime_adaptation_list = soup.find('td', text='Adaptation:').next_sibling
        anime_adaptation = []
        for x in range(len(list(anime_adaptation_list.children))):
            if str(list(anime_adaptation_list.children)[x]) == ', ':
                continue
            if list(anime_adaptation_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_adaptation_list.children)[x]['href']
            mal_id = re.search('/manga/(.*)/', link)
            anime_adaptation.append({'mal_id': int(mal_id.group(1)), 'link': link,
                                     'title': str(list(anime_adaptation_list.children)[x].get_text())})
        if not anime_adaptation:
            anime_adaptation = None
    except AttributeError:
        anime_adaptation = None

    try:
        anime_alternative_setting_list = soup.find('td', text='Alternative setting:').next_sibling
        anime_alternative_setting = []
        for x in range(len(list(anime_alternative_setting_list.children))):
            if str(list(anime_alternative_setting_list.children)[x]) == ', ':
                continue
            if list(anime_alternative_setting_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_alternative_setting_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_alternative_setting.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_alternative_setting_list.children)[x].get_text())})
        if not anime_alternative_setting:
            anime_alternative_setting = None
    except AttributeError:
        anime_alternative_setting = None

    try:
        anime_alternative_version_list = soup.find('td', text='Alternative version:').next_sibling
        anime_alternative_version = []
        for x in range(len(list(anime_alternative_version_list.children))):
            if str(list(anime_alternative_version_list.children)[x]) == ', ':
                continue
            if list(anime_alternative_version_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_alternative_version_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_alternative_version.append({'mal_id': int(mal_id.group(1)), 'link': link, 'title': str(
                list(anime_alternative_version_list.children)[x].get_text())})
        if not anime_alternative_version:
            anime_alternative_version = None
    except AttributeError:
        anime_alternative_version = None

    try:
        anime_sequel_list = soup.find('td', text='Sequel:').next_sibling
        anime_sequel = []
        for x in range(len(list(anime_sequel_list.children))):
            if str(list(anime_sequel_list.children)[x]) == ', ':
                continue
            if list(anime_sequel_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_sequel_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_sequel.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_sequel_list.children)[x].get_text())})
        if not anime_sequel:
            anime_sequel = None
    except AttributeError:
        anime_sequel = None

    try:
        anime_prequel_list = soup.find('td', text='Prequel:').next_sibling
        anime_prequel = []
        for x in range(len(list(anime_prequel_list.children))):
            if str(list(anime_prequel_list.children)[x]) == ', ':
                continue
            if list(anime_prequel_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_prequel_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_prequel.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_prequel_list.children)[x].get_text())})
        if not anime_prequel:
            anime_prequel = None
    except AttributeError:
        anime_prequel = None

    try:
        anime_side_story_list = soup.find('td', text='Side story:').next_sibling
        anime_side_story = []
        for x in range(len(list(anime_side_story_list.children))):
            if str(list(anime_side_story_list.children)[x]) == ', ':
                continue
            if list(anime_side_story_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_side_story_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_side_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_side_story_list.children)[x].get_text())})
        if not anime_side_story:
            anime_side_story = None
    except AttributeError:
        anime_side_story = None

    try:
        anime_spin_off_list = soup.find('td', text='Spin-off:').next_sibling
        anime_spin_off = []
        for x in range(len(list(anime_spin_off_list.children))):
            if str(list(anime_spin_off_list.children)[x]) == ', ':
                continue
            if list(anime_spin_off_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_spin_off_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_spin_off.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_spin_off_list.children)[x].get_text())})
        if not anime_spin_off:
            anime_spin_off = None
    except AttributeError:
        anime_spin_off = None

    try:
        anime_summary_list = soup.find('td', text='Summary:').next_sibling
        anime_summary = []
        for x in range(len(list(anime_summary_list.children))):
            if str(list(anime_summary_list.children)[x]) == ', ':
                continue
            if list(anime_summary_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_summary_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_summary.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_summary_list.children)[x].get_text())})
        if not anime_summary:
            anime_summary = None
    except AttributeError:
        anime_summary = None

    try:
        anime_character_list = soup.find('td', text='Character:').next_sibling
        anime_character = []
        for x in range(len(list(anime_character_list.children))):
            if str(list(anime_character_list.children)[x]) == ', ':
                continue
            if list(anime_character_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_character_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_character.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_character_list.children)[x].get_text())})
        if not anime_character:
            anime_character = None
    except AttributeError:
        anime_character = None

    try:
        anime_other_list = soup.find('td', text='Other:').next_sibling
        anime_other = []
        for x in range(len(list(anime_other_list.children))):
            if str(list(anime_other_list.children)[x]) == ', ':
                continue
            if list(anime_other_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_other_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_other.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_other_list.children)[x].get_text())})
        if not anime_other:
            anime_other = None
    except AttributeError:
        anime_other = None

    try:
        anime_full_story_list = soup.find('td', text='Full story:').next_sibling
        anime_full_story = []
        for x in range(len(list(anime_full_story_list.children))):
            if str(list(anime_full_story_list.children)[x]) == ', ':
                continue
            if list(anime_full_story_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_full_story_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_full_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_full_story_list.children)[x].get_text())})
        if not anime_full_story:
            anime_full_story = None
    except AttributeError:
        anime_full_story = None

    try:
        anime_parent_story_list = soup.find('td', text='Parent story:').next_sibling
        anime_parent_story = []
        for x in range(len(list(anime_parent_story_list.children))):
            if str(list(anime_parent_story_list.children)[x]) == ', ':
                continue
            if list(anime_parent_story_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_parent_story_list.children)[x]['href']
            mal_id = re.search('anime/(.*)/', link)
            anime_parent_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_parent_story_list.children)[x].get_text())})
        if not anime_parent_story:
            anime_parent_story = None
    except AttributeError:
        anime_parent_story = None

    relations = {
        'anime_adaptation': anime_adaptation,
        'anime_alternative_setting': anime_alternative_setting,
        'anime_alternative_version': anime_alternative_version,
        'anime_sequel': anime_sequel,
        'anime_prequel': anime_prequel,
        'anime_side_story': anime_side_story,
        'anime_spin_off': anime_spin_off,
        'anime_summary': anime_summary,
        'anime_other': anime_other,
        'anime_character': anime_character,
        'anime_full_story': anime_full_story,
        'anime_parent_story': anime_parent_story
    }

    final = {'relations': relations}

    for key, value in relations.items():
        if value is not None:
            return final

    final = None

    return final


def get_ost(soup):
    anime_endings = ''
    anime_openings = ''
    try:
        for x in range(len(list(soup.find('div', attrs={'class': 'theme-songs js-theme-songs opnening'}).children))):
            if list(soup.find('div', attrs={'class': 'theme-songs js-theme-songs opnening'}).children)[x].name == 'span':
                anime_openings = anime_openings + list(
                    soup.find('div', attrs={'class': 'theme-songs js-theme-songs opnening'}).children)[
                    x].get_text() + '\n'
        if anime_openings == '':
            anime_openings = None

    except AttributeError:
        anime_openings = None

    try:
        for x in range(len(list(soup.find('div', attrs={'class': 'theme-songs js-theme-songs ending'}).children))):
            if list(soup.find('div', attrs={'class': 'theme-songs js-theme-songs ending'}).children)[x].name == 'span':
                anime_endings = anime_endings + \
                                list(soup.find('div', attrs={'class': 'theme-songs js-theme-songs ending'}).children)[
                                    x].get_text() + '\n'
        if anime_endings == '':
            anime_endings = None
    except AttributeError:
        anime_endings = None

    osts = {
        'anime_openings': anime_openings,
        'anime_endings': anime_endings
    }

    return osts


def check_airing_status(anime_status):
    if "Currently Airing" in anime_status:
        return True
    else:
        return False


def get_minutes_per_episode(duration):
    total = 0.00
    # Calculate the total duration of the anime
    try:
        if 'min. per ep.' in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            return int(mins)
        elif 'min.' in duration and 'hr.' not in duration and 'sec' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            return int(mins)
        elif 'min.' in duration and 'hr.' in duration and 'sec' not in duration:
            temp = duration.split("hr.")
            mins = (int(''.join(filter(lambda x: x.isdigit(), temp[0]))) * 60) + int(
                ''.join(filter(lambda x: x.isdigit(), temp[1])))
            return int(mins)
        elif 'sec.' not in duration and 'hr.' in duration and 'min.' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            mins = int(mins) * 60
            return int(mins)
        elif 'sec.' in duration and 'hr.' not in duration and 'min.' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            mins = round(int(mins) / 60, 2)
            return int(mins)
    except TypeError:
        pass

    # Return total minutes
    return total


def calculate_total_length_mins(anime_duration, anime_episodes):
    total_mins = get_duration_mins_from_duration(anime_duration, anime_episodes)

    return total_mins


def get_aired_dates(anime_aired_string):
    raw = anime_aired_string.replace(',', '')

    if 'Not available' in raw:
        return {'air_start': 'None', 'air_start_known': 'None', 'air_end': 'None', 'air_end_known': 'None'}

    if 'to' in raw:
        split = raw.split(' to ')

        dates = get_dates(split[0])

        air_start = dates[0]
        air_start_known = dates[1]

        if '?' in split[1]:
            air_end = None
            air_end_known = None
        else:
            dates = get_dates(split[1])

            air_end = dates[0]
            air_end_known = dates[1]

    else:
        dates = get_dates(raw)

        air_start = dates[0]
        air_start_known = dates[1]

        air_end = None
        air_end_known = None

    aired_dates = {
        'air_start': str(air_start),
        'air_start_known': str(air_start_known),
        'air_end': str(air_end),
        'air_end_known': str(air_end_known)
    }

    return aired_dates


# ###########################################################################
# ###########################################################################
#
# FUNCTIONS FOR MANGA
#
# ###########################################################################
# ###########################################################################


def get_manga_titles(soup):
    # get the titles
    try:
        manga_title = soup.h1.span.text
    except AttributeError:
        manga_title = None

    try:
        manga_title_english = soup.find('span', text="English:").parent.text \
            .replace('\n', '') \
            .replace('English: ', '') \
            .strip(' ')
    except AttributeError:
        manga_title_english = None

    try:
        manga_title_japanese = soup.find('span', text="Japanese:").parent.text \
            .replace('\n', '') \
            .replace('Japanese: ', '') \
            .strip(' ')
    except AttributeError:
        manga_title_japanese = None

    try:
        manga_title_synonyms = soup.find('span', text="Synonyms:").parent.text \
            .replace('\n', '') \
            .replace('Synonyms: ', '') \
            .strip(' ')
    except AttributeError:
        manga_title_synonyms = None

    titles = {
        'manga_title': manga_title,
        'manga_title_english': manga_title_english,
        'manga_title_japanese': manga_title_japanese,
        'manga_title_synonyms': manga_title_synonyms
    }

    return titles


def get_manga_information(soup):
    try:
        manga_image_src = soup.find('img', attrs={'itemprop': 'image'})['src']
    except TypeError:
        manga_image_src = None

    manga_type = soup.find('span', text='Type:').parent.text \
        .replace('\n', '') \
        .replace('Type:', '') \
        .replace(' ', '')

    try:
        manga_volumes = int(soup.find('span', text='Volumes:').parent.text
                            .replace('\n', '')
                            .replace('Volumes:', '')
                            .replace(' ', ''))
    except ValueError:
        manga_volumes = None

    try:
        manga_chapters = int(soup.find('span', text='Chapters:').parent.text
                             .replace('\n', '')
                             .replace('Chapters:', '')
                             .replace(' ', ''))
    except ValueError:
        manga_chapters = None

    manga_status = soup.find('span', text='Status:').parent.text \
        .replace('\n', '') \
        .replace('Status:', '') \
        .strip(' ')

    manga_published_string = soup.find('span', text='Published:').parent.text \
        .replace('\n', '') \
        .replace('Published:', '') \
        .strip(' ')

    manga_genres = soup.find('span', text='Genres:').parent.get_text() \
        .replace('\n', '') \
        .replace('Genres:', '')

    manga_authors = re.sub(' +', ' ', soup.find('span', text='Authors:').parent.text
                           .replace('\n', '')
                           .replace('Authors:', '')
                           .strip(' '))
    if manga_authors == 'None':
        manga_authors = None

    manga_serialization = re.sub(' +', ' ', soup.find('span', text='Serialization:').parent.text
                                 .replace('\n', '')
                                 .replace('Serialization:', '')
                                 .strip(' '))
    if manga_serialization == 'None':
        manga_serialization = None

    info = {
        'manga_image_src': manga_image_src,
        'manga_type': manga_type,
        'manga_volumes': manga_volumes,
        'manga_chapters': manga_chapters,
        'manga_status': manga_status,
        'manga_published_string': manga_published_string,
        'manga_genres': manga_genres,
        'manga_authors': manga_authors,
        'manga_serialization': manga_serialization
    }

    return info


def check_publishing_status(manga_status):
    if "Publishing" in manga_status:
        return True
    else:
        return False


def get_manga_statistics(soup):
    try:
        manga_score = float(soup.find('span', attrs={'itemprop': 'ratingValue'}).text)
    except AttributeError:
        try:
            manga_score = float(soup.find('span', text='Score:').next_sibling.next_sibling.text)
        except ValueError:
            manga_score = None
        except AttributeError:
            manga_score = None
            print('Something went wrong again!')

    try:
        manga_scored_by = int(soup.find('span', attrs={'itemprop': 'ratingCount'}).text
                              .replace(',', ''))
    except AttributeError:
        try:
            manga_scored_by = int(soup.find('span', text='Score:')
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .next_sibling
                                  .text)
        except ValueError:
            manga_scored_by = 0

            if 'scored by ' in str(soup.td):
                td = str(soup.td)
                match = re.search('scored by (\d+)', td)
                if match:
                    manga_scored_by = int(match.group(1))

    remove = soup.find('span', text='Ranked:').parent.find('sup')
    remove.extract()
    remove = soup.find('span', text='Ranked:').parent.find('div')
    remove.extract()

    if "N/A" not in soup.find('span', text='Ranked:').parent.text:
        manga_ranked = int(soup.find('span', text='Ranked:').parent.text
                           .replace('\n', '')
                           .replace('Ranked:', '')
                           .replace(' ', '')
                           .replace('#', ''))
    else:
        manga_ranked = None

    manga_popularity = int(soup.find('span', text='Popularity:').parent.text
                           .replace('\n', '')
                           .replace('Popularity:', ' ')
                           .replace('#', '')
                           .strip(' '))

    manga_members = int(soup.find('span', text='Members:').parent.text
                        .replace('\n', '')
                        .replace('Members:', '')
                        .replace(' ', '')
                        .replace(',', ''))

    manga_favorites = int(soup.find('span', text='Favorites:').parent.text
                          .replace('\n', '')
                          .replace('Favorites:', '')
                          .replace(' ', '')
                          .replace(',', ''))

    stats = {
        'manga_score': manga_score,
        'manga_scored_by': manga_scored_by,
        'manga_ranked': manga_ranked,
        'manga_popularity': manga_popularity,
        'manga_members': manga_members,
        'manga_favorites': manga_favorites,
    }

    return stats


def get_manga_description(soup):
    try:
        manga_synopsis = soup.find('span', attrs={'itemprop': 'description'}).get_text()
    except AttributeError:
        manga_synopsis = None

    try:
        background = soup.find_all('table')[2].find('td').find_all('h2')[1].next_sibling
    except IndexError:
        background = soup.find('h2', attrs={'style': 'margin-top: 15px;'}).next_sibling

    manga_background = ''

    while background.next_sibling is not None:
        if background.name == 'i':
            manga_background += background.text
        else:
            manga_background += str(background)
        if background.next_sibling.name == 'div' or background.next_sibling.name == 'a':
            break
        else:
            background = background.next_sibling
    manga_background = manga_background.replace('<br/>', '').replace('\n', '')

    if manga_background.__contains__('No background information'):
        manga_background = None

    description = {
        'manga_synopsis': manga_synopsis,
        'manga_background': manga_background
    }

    return description


def get_manga_relations(soup):
    try:
        anime_adaptation_list = soup.find('td', text='Adaptation:').next_sibling
        manga_adaptation = []
        for x in range(len(list(anime_adaptation_list.children))):
            if str(list(anime_adaptation_list.children)[x]) == ', ':
                continue
            if list(anime_adaptation_list.children)[x]['href'] == '/anime//':
                continue
            link = 'https://myanimelist.net' + list(anime_adaptation_list.children)[x]['href']
            mal_id = re.search('/anime/(.*)/', link)
            manga_adaptation.append({'mal_id': int(mal_id.group(1)), 'link': link,
                                     'title': str(list(anime_adaptation_list.children)[x].get_text())})
        if not manga_adaptation:
            manga_adaptation = None
    except AttributeError:
        manga_adaptation = None

    try:
        anime_alternative_setting_list = soup.find('td', text='Alternative setting:').next_sibling
        manga_alternative_setting = []
        for x in range(len(list(anime_alternative_setting_list.children))):
            if str(list(anime_alternative_setting_list.children)[x]) == ', ':
                continue
            if list(anime_alternative_setting_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_alternative_setting_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_alternative_setting.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_alternative_setting_list.children)[x].get_text())})
        if not manga_alternative_setting:
            manga_alternative_setting = None
    except AttributeError:
        manga_alternative_setting = None

    try:
        anime_alternative_version_list = soup.find('td', text='Alternative version:').next_sibling
        manga_alternative_version = []
        for x in range(len(list(anime_alternative_version_list.children))):
            if str(list(anime_alternative_version_list.children)[x]) == ', ':
                continue
            if list(anime_alternative_version_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_alternative_version_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_alternative_version.append({'mal_id': int(mal_id.group(1)), 'link': link, 'title': str(
                list(anime_alternative_version_list.children)[x].get_text())})
        if not manga_alternative_version:
            manga_alternative_version = None
    except AttributeError:
        manga_alternative_version = None

    try:
        anime_sequel_list = soup.find('td', text='Sequel:').next_sibling
        manga_sequel = []
        for x in range(len(list(anime_sequel_list.children))):
            if str(list(anime_sequel_list.children)[x]) == ', ':
                continue
            if list(anime_sequel_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_sequel_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_sequel.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_sequel_list.children)[x].get_text())})
        if not manga_sequel:
            manga_sequel = None
    except AttributeError:
        manga_sequel = None

    try:
        anime_prequel_list = soup.find('td', text='Prequel:').next_sibling
        manga_prequel = []
        for x in range(len(list(anime_prequel_list.children))):
            if str(list(anime_prequel_list.children)[x]) == ', ':
                continue
            if list(anime_prequel_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_prequel_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_prequel.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_prequel_list.children)[x].get_text())})
        if not manga_prequel:
            manga_prequel = None
    except AttributeError:
        manga_prequel = None

    try:
        anime_side_story_list = soup.find('td', text='Side story:').next_sibling
        manga_side_story = []
        for x in range(len(list(anime_side_story_list.children))):
            if str(list(anime_side_story_list.children)[x]) == ', ':
                continue
            if list(anime_side_story_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_side_story_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_side_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_side_story_list.children)[x].get_text())})
        if not manga_side_story:
            manga_side_story = None
    except AttributeError:
        manga_side_story = None

    try:
        anime_spin_off_list = soup.find('td', text='Spin-off:').next_sibling
        manga_spin_off = []
        for x in range(len(list(anime_spin_off_list.children))):
            if str(list(anime_spin_off_list.children)[x]) == ', ':
                continue
            if list(anime_spin_off_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_spin_off_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_spin_off.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_spin_off_list.children)[x].get_text())})
        if not manga_spin_off:
            manga_spin_off = None
    except AttributeError:
        manga_spin_off = None

    try:
        anime_summary_list = soup.find('td', text='Summary:').next_sibling
        manga_summary = []
        for x in range(len(list(anime_summary_list.children))):
            if str(list(anime_summary_list.children)[x]) == ', ':
                continue
            if list(anime_summary_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_summary_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_summary.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_summary_list.children)[x].get_text())})
        if not manga_summary:
            manga_summary = None
    except AttributeError:
        manga_summary = None

    try:
        anime_character_list = soup.find('td', text='Character:').next_sibling
        manga_character = []
        for x in range(len(list(anime_character_list.children))):
            if str(list(anime_character_list.children)[x]) == ', ':
                continue
            if list(anime_character_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_character_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_character.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_character_list.children)[x].get_text())})
        if not manga_character:
            manga_character = None
    except AttributeError:
        manga_character = None

    try:
        anime_other_list = soup.find('td', text='Other:').next_sibling
        manga_other = []
        for x in range(len(list(anime_other_list.children))):
            if str(list(anime_other_list.children)[x]) == ', ':
                continue
            if list(anime_other_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_other_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_other.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_other_list.children)[x].get_text())})
        if not manga_other:
            manga_other = None
    except AttributeError:
        manga_other = None

    try:
        anime_full_story_list = soup.find('td', text='Full story:').next_sibling
        manga_full_story = []
        for x in range(len(list(anime_full_story_list.children))):
            if str(list(anime_full_story_list.children)[x]) == ', ':
                continue
            if list(anime_full_story_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_full_story_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_full_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_full_story_list.children)[x].get_text())})
        if not manga_full_story:
            manga_full_story = None
    except AttributeError:
        manga_full_story = None

    try:
        anime_parent_story_list = soup.find('td', text='Parent story:').next_sibling
        manga_parent_story = []
        for x in range(len(list(anime_parent_story_list.children))):
            if str(list(anime_parent_story_list.children)[x]) == ', ':
                continue
            if list(anime_parent_story_list.children)[x]['href'] == '/manga//':
                continue
            link = 'https://myanimelist.net' + list(anime_parent_story_list.children)[x]['href']
            mal_id = re.search('manga/(.*)/', link)
            manga_parent_story.append(
                {'mal_id': int(mal_id.group(1)), 'link': link,
                 'title': str(list(anime_parent_story_list.children)[x].get_text())})
        if not manga_parent_story:
            manga_parent_story = None
    except AttributeError:
        manga_parent_story = None

    relations = {
        'manga_adaptation': manga_adaptation,
        'manga_alternative_setting': manga_alternative_setting,
        'manga_alternative_version': manga_alternative_version,
        'manga_sequel': manga_sequel,
        'manga_prequel': manga_prequel,
        'manga_side_story': manga_side_story,
        'manga_spin_off': manga_spin_off,
        'manga_summary': manga_summary,
        'manga_other': manga_other,
        'manga_character': manga_character,
        'manga_full_story': manga_full_story,
        'manga_parent_story': manga_parent_story
    }

    final = {'relations': relations}

    for key, value in relations.items():
        if value is not None:
            return final

    final = None

    return final


def get_published_dates(anime_aired_string):
    raw = anime_aired_string.replace(',', '')

    if 'Not available' in raw:
        return {'air_start': 'None', 'air_start_known': 'None', 'air_end': 'None', 'air_end_known': 'None'}

    if 'to' in raw:
        split = raw.split(' to ')

        dates = get_manga_dates(split[0])

        air_start = dates[0]
        air_start_known = dates[1]

        if '?' in split[1]:
            air_end = None
            air_end_known = None
        else:
            dates = get_manga_dates(split[1])

            air_end = dates[0]
            air_end_known = dates[1]

    else:
        dates = get_manga_dates(raw)

        air_start = dates[0]
        air_start_known = dates[1]

        air_end = None
        air_end_known = None

    aired_dates = {
        'air_start': str(air_start),
        'air_start_known': str(air_start_known),
        'air_end': str(air_end),
        'air_end_known': str(air_end_known)
    }

    return aired_dates


# ###########################################################################
# ###########################################################################
#
# FUNCTIONS FOR CHARACTERS
#
# ###########################################################################
# ###########################################################################


def get_character_name(soup):
    try:
        name = soup.h1.text
        character_name = re.sub(' +', ' ', name)
        if character_name.endswith(' '):
            character_name = character_name[:-1]
        if character_name.startswith(' '):
            character_name = character_name[1:]
    except AttributeError:
        character_name = None

    return character_name


def get_character_info(soup):
    if 'Add Picture' not in str(soup.find_all('div', {'style': 'text-align: center;'})):
        try:
            character_image_src = soup.find_all('img')[1]['src']
        except TypeError:
            character_image_src = None
    else:
        character_image_src = None

    character_member_favorites = 0
    if 'Member Favorites:' in str(soup.td):
        td = str(soup.td)
        match = re.search('Member Favorites: (\d+),(\d+)', td)
        if match:
            character_member_favorites = (int(match.group(1)) * 1000) + int(match.group(2))

        else:
            match = re.search('Member Favorites: (\d+)', td)
            if match:
                character_member_favorites = int(match.group(1))

    info = {
        'character_image_src': character_image_src,
        'character_member_favorites': character_member_favorites,
    }

    return info


def get_character_description(soup):
    background = soup.find('div', {'class': 'breadcrumb'}).next_sibling.next_sibling.next_sibling
    character_description = ''

    while True:
        try:
            if 'Voice Actors' in background.text:
                character_description += background.text
                break
            else:
                character_description += background.text
        except AttributeError:
            try:
                if 'Voice Actors' in background:
                    character_description += background
                    break
                else:
                    character_description += background
            except TypeError:
                background = soup.html.next_sibling

        background = background.next_sibling

    character_description = character_description.split('Voice Actors', 1)[0]

    description = {
        'character_description': character_description,
    }

    return description


def get_character_voice_actors(soup):
    character_voice_actors = ''
    x = 0
    while True:
        titles = soup.find_all('div', {'class': 'normal_header'})

        if 'Voice Actors' in titles[x].text:
            if titles[x].next_sibling.next_sibling.name == 'table':
                node = titles[x].next_sibling.next_sibling

                y = 0
                while True:
                    if 'Recent Featured Articles' in str(node) or 'googletag.cmd.push' in str(node):
                        break
                    try:
                        character_voice_actors += node.text
                    except AttributeError:
                        try:
                            node = node.next_sibling
                            continue
                        except AttributeError:
                            break

                    node = node.next_sibling

                    y += 1
            break
        x += 1

    character_voice_actors = re.sub(r'\n\s*\n', '\n\n', character_voice_actors)

    if character_voice_actors == "":
        character_voice_actors = None

    return character_voice_actors


def get_character_roles(soup):
    anime_roles = []
    manga_roles = []
    x = 0
    while True:
        titles = soup.find_all('div', {'class': 'normal_header'})

        try:
            if 'Animeography' in titles[x].text:
                table = titles[x].next_sibling.next_sibling
                for item in table.find_all('td'):
                    if 'img' in str(item.find('a')):
                        continue
                    url = item.find('a')['href']
                    mal_id = re.search('anime/(.*)/', url)

                    anime_roles.append({'mal_id': int(mal_id.group(1)),
                                        'title': item.find('a').text,
                                        'link': url,
                                        'role': item.find('small').text})

            if 'Mangaography' in titles[x].text:
                table = titles[x].next_sibling.next_sibling
                for item in table.find_all('td'):
                    if 'img' in str(item.find('a')):
                        continue
                    url = item.find('a')['href']
                    mal_id = re.search('manga/(.*)/', url)

                    manga_roles.append({'mal_id': int(mal_id.group(1)),
                                        'title': item.find('a').text,
                                        'link': url,
                                        'role': item.find('small').text})
        except IndexError:
            break

        x += 1

    if len(anime_roles) == 0:
        anime_roles = None
    if len(manga_roles) == 0:
        manga_roles = None

    return anime_roles, manga_roles


# ###########################################################################
# ###########################################################################
#
# FUNCTIONS FOR FILES
#
# ###########################################################################
# ###########################################################################


def get_cover_image(url, name):
    while True:
        try:
            r = requests.get(url, allow_redirects=True)
            open(name, 'wb').write(r.content)
            break
        except requests.ConnectionError:
            print('<-Connection Error (Image)-> reconnecting...')
            time.sleep(5)


def convert_to_readable_json(filename):
    while True:
        with open(filename, "r") as file:
            content = file.read()
            if content.endswith(",]}"):
                print('Converting from broken JSON...')
                with open(filename, "w") as finishedJson:
                    final = content[:-3] + ']}'
                    finishedJson.write(final)
            if content.endswith(","):
                print('Converting from appendable JSON...')
                with open(filename, "w") as finishedJson:
                    final = content[:-1] + ']}'
                    finishedJson.write(final)
            else:
                print('JSON is readable.')
                break


def convert_to_appendable_json(filename):
    while True:
        with open(filename, "r") as file:
            content = file.read()
            if content.endswith(",]}"):
                print('Converting from readable JSON...')
                with open(filename, "w") as finishedJson:
                    final = content[:-3] + ','
                    finishedJson.write(final)
            elif content.endswith("]}"):
                print('Converting from readable JSON...')
                with open(filename, "w") as finishedJson:
                    final = content[:-2] + ','
                    finishedJson.write(final)
            else:
                print('JSON is appendable.')
                break
