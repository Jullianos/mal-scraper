import json

from datetime import datetime


# Calculate the total minutes one anime lasts
# Params: duration of one episode of the anime and the number of episodes the anime has
def get_duration_mins_from_duration(duration, episodes):
    total = 0.00
    # Calculate the total duration of the anime
    try:
        if 'min. per ep.' in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            total += int(mins) * episodes
        elif 'min.' in duration and 'hr.' not in duration and 'sec' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            total += int(mins) * episodes
        elif 'min.' in duration and 'hr.' in duration and 'sec' not in duration:
            temp = duration.split("hr.")
            mins = (int(''.join(filter(lambda x: x.isdigit(), temp[0]))) * 60) + int(
                ''.join(filter(lambda x: x.isdigit(), temp[1])))
            total += int(mins) * episodes
        elif 'sec.' not in duration and 'hr.' in duration and 'min.' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            mins = int(mins) * 60
            total += int(mins) * episodes
        elif 'sec.' in duration and 'hr.' not in duration and 'min.' not in duration:
            mins = ''.join(filter(lambda x: x.isdigit(), duration))
            mins = round(int(mins) / 60, 2)
            total += round(float(mins), 2) * episodes
    except TypeError:
        pass
        
    # Return total minutes
    return total


def get_dates(date_string):
    try:
        air = datetime.strptime(date_string, '%b %d %Y')
        air_known = ['year', 'month', 'day']
    except ValueError:
        try:
            air = datetime.strptime(date_string, '%Y')
            air_known = ['year']
        except ValueError:
            air = datetime.strptime(date_string, '%b %Y')
            air_known = ['year', 'month']

    dates = [air, air_known]

    return dates


def get_manga_dates(date_string):
    try:
        air = datetime.strptime(date_string, '%b %d %Y')
        air_known = ['year', 'month', 'day']
    except ValueError:
        try:
            air = datetime.strptime(date_string, '%Y')
            air_known = ['year']
        except ValueError:
            try:
                air = datetime.strptime(date_string, '%b %Y')
                air_known = ['year', 'month']
            except ValueError:
                try:
                    air = datetime.strptime(date_string, ' %d %Y')
                    air_known = ['year']
                except ValueError:
                    try:
                        air = datetime.strptime(date_string, '%d %Y')
                        air_known = ['year']
                    except ValueError:
                        dates = [None, None]
                        return dates

    dates = [air, air_known]

    return dates
