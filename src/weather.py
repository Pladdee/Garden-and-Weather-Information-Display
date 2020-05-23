from datetime import *
import time as t
import pytemperature
import requests
import sqlite3
from src.mqtt import cursor, db
from Credentials.credentials import *

weekdays = {
    0: 'Montag',
    1: 'Dienstag',
    2: 'Mittwoch',
    3: 'Donnerstag',
    4: 'Freitag',
    5: 'Samstag',
    6: 'Sonntag',
}

weather_to_value = {
    "Clear": 1,
    "few clouds": 1.25,
    "scattered clouds": 1.5,
    "broken clouds": 1.75,
    "overcast clouds": 2,
    "Rain": 2,
    "Drizzle": 2,
    "Snow": 2,
    "Thunderstorm": 2,
    "Fog": 1.75,
}


class Day:
    def __init__(self):
        self.date = None
        self.weekday = None
        self.max_temp = -50
        self.min_temp = 9999
        self.description = None
        self.rain = {}
        self.snow = {}
        self.thunderstorms = {}

    def __str__(self):
        return self.weekday + ', ' + self.date + ': ' + str(self.max_temp) + '/' + str(self.min_temp) + ', ' + \
               str(self.description) + '\nRain: ' + str(self.rain) + '\nSnow: ' + str(self.snow) + \
               '\nThunderstorm: ' + str(self.thunderstorms)


class Today(Day):
    def __init__(self):
        Day.__init__(self)
        self.current_temperature = 0
        self.current_description = None
        self.time_of_last_measure = None
        self.initialized = False


def calculate_weather(indicators, i, weather_indicator, current_time):
    weather_measure_count = 5 - indicators['Fog']
    weather_indicator = weather_indicator / weather_measure_count

    # catch extreme cases
    if indicators['Snow'] >= 2:
        days.get(i).description = 'Snow'
    elif indicators['Thunderstorm'] >= 2:
        days.get(i).description = 'Thunderstorm'
    elif indicators['Fog'] >= 2:
        days.get(i).description = 'Fog'
    elif indicators['Rain'] > 0:
        if indicators['Rain'] == 1:
            if indicators['Thunderstorm'] == 1:
                days.get(i).description = 'Thunderstorm'
            elif indicators['Snow'] == 1:
                days.get(i).description = 'Snow'
            elif weather_indicator > 1.6:
                days.get(i).description = 'Rain'
            else:
                calculate = True
        elif indicators['Rain'] >= 2:
            days.get(i).description = 'Rain'
    else:
        if weather_indicator < 1.2:
            days.get(i).description = 'Clear'
        elif weather_indicator < 1.5:
            days.get(i).description = 'few clouds'
        elif weather_indicator <= 1.7:
            days.get(i).description = 'scattered clouds'
        elif weather_indicator < 1.9:
            days.get(i).description = 'broken clouds'
        else:
            days.get(i).description = 'overcast clouds'

    print(weather_indicator)
    print('calculated: ' + days.get(i).description)
    print(15 * '-')

    cursor.execute(
        "INSERT INTO weather(weather_description, time, date, time_of_receive) VALUES(?, ?, ?, ?);",
        (days.get(i).description, 'DAY AVERAGE', days.get(i).date,
         current_time.strftime('%H:%M')))


day0 = Today()
day1 = Day()
day2 = Day()
day3 = Day()
day4 = Day()

days = {0: day0, 1: day1, 2: day2, 3: day3, 4: day4}

url = 'http://api.openweathermap.org/data/2.5/forecast?appid=' + api_key + '&q=' + city

cursor.execute("CREATE TABLE IF NOT EXISTS weather"
               "(id INTEGER PRIMARY KEY, weather_description TEXT, time TEXT, date TEXT, time_of_receive TEXT);")


def get_weather():
    response = requests.get(url).json()

    if response["cod"] != "404":
        # returns list of 3-hour-measurements
        forecast_list = response["list"]
        first_data_packet = forecast_list[0]

        # Initialization of today
        date_of_today = datetime.fromtimestamp(first_data_packet['dt'])
        day0.date, day0.time_of_last_measure = date_of_today.strftime('%d.%m.%Y %H:%M').split(" ")
        day0.current_temperature = int(pytemperature.k2c(first_data_packet['main']['temp']))
        today_weather = first_data_packet['weather'][0]['main']
        if today_weather == 'Clouds':
            today_weather = first_data_packet['weather'][0]['description']
        day0.current_description = today_weather

        if day0.date == day1.date:
            # New Day
            day0.description = day1.description
            day0.min_temp = day1.min_temp
            day0.max_temp = day1.max_temp

        # Reset days
        for j in range(1, 5):
            days[j].date = (date_of_today + timedelta(days=j)).strftime('%d.%m.%Y')
            days[j].max_temp = -50
            days[j].min_temp = 9999

        for j in range(5):
            days[j].weekday = weekdays.get((list(weekdays.keys())[list(weekdays.values())
                                            .index(weekdays.get(date_of_today.weekday()))] + j) % 7)
            days[j].rain = {}
            days[j].snow = {}
            days[j].thunderstorms = {}

        # only interested in weather descriptions between 5AM and 23PM
        min_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0).time()
        max_time = datetime.now().replace(hour=23, minute=0, second=0, microsecond=0).time()

        # iterate through the whole dataset
        dates = [None, None, None, None, None]
        for i in range(5):
            dates[i] = days[i].date

        current_date = day0.date
        weather_indicator = 0
        indicators = {'Rain': 0, 'Snow': 0, 'Thunderstorm': 0, 'Fog': 0}
        current_time = datetime.now()
        day0.time_of_last_measure = current_time.strftime("%H:%M")

        for measurement in range(len(forecast_list)):
            current = forecast_list[measurement]
            date_time = datetime.fromtimestamp(current['dt'])
            iterate_time = date_time.time()
            iterate_date = date_time.strftime('%d.%m.%Y')

            for i in range(5):
                if iterate_date == dates[i]:
                    if iterate_date != current_date:  # new day?
                        calculate_weather(indicators, i - 1, weather_indicator, current_time)
                        indicators['Rain'] = 0
                        indicators['Snow'] = 0
                        indicators['Thunderstorm'] = 0
                        indicators['Fog'] = 0
                        weather_indicator = 0
                        current_date = iterate_date

                    current_temp = int(pytemperature.k2c(current['main']['temp']))
                    if current_temp > days.get(i).max_temp:
                        days.get(i).max_temp = current_temp
                    elif current_temp < days.get(i).min_temp:
                        days.get(i).min_temp = current_temp

                    if iterate_date == day0.date:
                        if day0.initialized:
                            break
                    # Weather
                    current_description = current['weather'][0]['main']
                    # catch "extreme situations" and save their action time
                    if current_description == 'Rain':
                        days.get(i).rain.update({iterate_time.strftime('%H:%M'): current['rain']['3h']})
                    elif current_description == 'Snow':
                        days.get(i).snow.update({iterate_time.strftime('%H:%M'): current['snow']['3h']})
                    elif current_description == 'Thunderstorm':
                        days.get(i).thunderstorms.update({iterate_time.strftime('%H:%M'): current['weather'][0]
                        ['description']})

                    # For calculation of average weather for the day; Just look at the times of desire
                    if min_time <= iterate_time < max_time:
                        # group smoke, haze, dust, sand, ... to Fog
                        if current_description != 'Clouds' or current_description != 'Clear' \
                                and current_description != 'Rain' and current_description != 'Snow' \
                                and current_description != 'Thunderstorm':
                            current_description == 'Fog'

                        # 'Clouds' is too general
                        if current_description == 'Clouds':
                            current_description = current['weather'][0]['description']
                        # add value of corresponding weather description to our calculation var
                        weather_indicator += weather_to_value.get(current_description)
                        # if description is an extreme weather, save it for days weather calculation
                        if current_description in indicators:
                            indicators[current_description] += 1
                        print(current_description)
                    cursor.execute(
                        "INSERT INTO weather(weather_description, time, date, time_of_receive) VALUES(?, ?, ?, ?);",
                        (current_description, iterate_time.strftime('%H:%M'),
                         iterate_date, current_time.strftime('%H:%M')))
                    break
        calculate_weather(indicators, 4, weather_indicator, current_time)

        # Debugging purpose
        for j in range(5):
            print(days.get(j))
        day0.initialized = True
        db.commit()
    else:
        print(" City Not Found ")


if __name__ == '__main__':
    get_weather()
