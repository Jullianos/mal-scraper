import json
import shutil

import anime_scraper
from core.utility.functions import convert_to_readable_json

franchises_filename = 'json/Franchises/Franchises.json'
franchises_filename_fixed = 'json/Franchises/FranchisesFixed.json'
franchises_filename_final = 'json/Franchises/FranchisesFinal.json'
original_anime_filename = 'json/Anime/AnimeDataNewAnime-Main.json'
anime_filename = original_anime_filename[:-5] + '-EDITED.json'


def generate_franchises():
    shutil.copyfile(original_anime_filename, anime_filename)
    convert_to_readable_json(filename=anime_filename)

    with open(anime_filename, 'r') as file:
        data = json.load(file)

    print('Total anime: ' + str(len(data['data'])))
    total = len(data['data'])

    all_anime = data['data']

    franchises = []
    jump = False

    count = 0
    for anime in all_anime:
        for franchise in franchises:
            for title in franchise['franchise_titles']:
                if title['relations'] is not None:
                    for relation in title['relations']:
                        if str(relation) == 'anime_adaptation' or str(relation) == 'anime_character':
                            continue
                        if title['relations'][str(relation)] is not None:
                            for item in title['relations'][str(relation)]:
                                if item['mal_id'] == anime['anime_mal_id']:
                                    franchise['franchise_titles'].append(anime)
                                    jump = True
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
            else:
                continue
            break

        count += 1
        print(str(count) + '/' + str(total))

        if jump:
            jump = False
            continue

        item = {'franchise_name': anime['anime_title'], 'mal_id': anime['anime_mal_id'], 'franchise_titles': [anime]}
        franchises.append(item)

    with open(franchises_filename, 'w') as file:
        file.write(json.dumps(franchises))


def fix_franchises():
    with open(franchises_filename, 'r') as file:
        franchises = json.load(file)

    total = len(franchises)

    count = 0
    for current_franchise in franchises:
        for current_title in current_franchise['franchise_titles']:
            for franchise in franchises:
                if franchise != current_franchise:
                    for title in franchise['franchise_titles']:
                        if title['relations'] is not None:
                            for relation in title['relations']:
                                if str(relation) == 'anime_adaptation' or str(relation) == 'anime_character':
                                    continue
                                if title['relations'][str(relation)] is not None:
                                    for item in title['relations'][str(relation)]:
                                        if str(relation) == 'anime_adaptation' or str(relation) == 'anime_character' or str(relation) == 'anime_other':
                                            continue
                                        if item['mal_id'] == current_title['anime_mal_id']:
                                            current_franchise['franchise_titles'] = \
                                                current_franchise['franchise_titles'] + franchise['franchise_titles']
                                            franchises.remove(franchise)
                                            break
                                    else:
                                        continue
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
            else:
                continue
            break

        count += 1
        print(str(count) + '/' + str(total))

    with open('json/Franchises/FranchisesFixed.json', 'w') as finished_file:
        finished_file.write(json.dumps(franchises))


def add_franchises_stats():
    with open(franchises_filename_fixed, 'r') as file:
        franchises = json.load(file)

    total = len(franchises)

    highest_score = 0
    total_episodes = 0
    total_minutes = 0
    total_titles = 0

    count = 0
    for franchise in franchises:
        for title in franchise['franchise_titles']:
            if title['anime_score']:
                if title['anime_score'] > highest_score:
                    highest_score = title['anime_score']

            if title['anime_episodes']:
                total_episodes += title['anime_episodes']

            if title['total_time_mins']:
                total_minutes += title['total_time_mins']

            total_titles += 1

        franchise['highest_score'] = highest_score
        franchise['total_episodes'] = total_episodes
        franchise['total_minutes'] = total_minutes
        franchise['total_titles'] = total_titles
        highest_score = 0
        total_episodes = 0
        total_minutes = 0
        total_titles = 0

        count += 1
        print(str(count) + '/' + str(total))

    with open(franchises_filename_final, 'w') as finished_file:
        finished_file.write(json.dumps(franchises))


generate_franchises()
fix_franchises()
add_franchises_stats()


print('Done!')


# print('###############################################################################################################')
# print('###############################################################################################################')
# print('###############################################################################################################')
# with open(franchises_filename_final, 'r') as file:
#     jsont = json.load(file)
#
#     print(len(jsont))
#     count = 0
#
#     for franchise in jsont:
#         # count += 1
#         # if count > 30:
#         #     break
#         print(franchise['franchise_name'])
#         for title in franchise['franchise_titles']:
#             print('\t' + str(title['anime_title']))

print('###############################################################################################################')
print('###############################################################################################################')
print('###############################################################################################################')
# with open(franchises_filename, 'r') as file2:
#     franchises = json.load(file2)
#
#     print(len(franchises))
#     count = 0
#
#     for franchise in franchises:
#         # count += 1
#         # if count > 30:
#         #     break
#         print(franchise['franchise_name'])
#         for title in franchise['franchise_titles']:
#             print('\t' + str(title['anime_title']))
