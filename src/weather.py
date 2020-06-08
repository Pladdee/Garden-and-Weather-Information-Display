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


class Day:
    def __init__(self):
        self.date = None
        self.weekday = None
        self.max_temp = -50
        self.min_temp = 9999
        self.description = None
        self.rain_amount = 0
        self.wind_speed = -1
        self.wind_direction = None

    def __str__(self):
        return self.weekday + ', ' + self.date + ': ' + str(self.max_temp) + '°C/' + str(self.min_temp) + '°C, ' + \
               str(self.description) + '\nRain: ' + str(self.rain_amount) + '\nWind: ' + str(self.wind_speed) + \
               ' ' + self.wind_direction


class Today(Day):
    def __init__(self):
        Day.__init__(self)
        self.current_temperature = 0
        self.current_wind_speed = -1
        self.current_description = None
        self.time_of_last_measure = None


day0 = Today()
day1 = Day()
day2 = Day()
day3 = Day()
day4 = Day()

days = {0: day0, 1: day1, 2: day2, 3: day3, 4: day4}

url = 'http://api.openweathermap.org/data/2.5/onecall?lat=' + str(lat) + '&lon=' + str(lon) + '&appid=' + api_key + \
      '&units=metric'


def get_weather():
    response = requests.get(url).json()

    if "cod" not in response:
        # pick current section & save date, time, temperature, weather description, wind speed
        current_weather_cast = response['current']
        date_of_today = datetime.fromtimestamp(current_weather_cast['dt'])
        day0.date, day0.time_of_last_measure = date_of_today.strftime('%d.%m.%Y %H:%M').split(" ")
        day0.current_temperature = round(current_weather_cast['temp'])
        day0.current_description = current_weather_cast['weather'][0]['main']
        if day0.current_description == 'Clouds':
            day0.current_description = current_weather_cast['weather'][0]['description']
        day0.current_wind_speed = current_weather_cast['wind_speed']

        # Reset days
        for j in range(5):
            days[j].date = (date_of_today + timedelta(days=j)).strftime('%d.%m.%Y')
            days[j].max_temp = -50
            days[j].min_temp = 9999
            days[j].weekday = weekdays.get((list(weekdays.keys())[list(weekdays.values())
                                            .index(weekdays.get(date_of_today.weekday()))] + j) % 7)
            days[j].rain_amount = 0
            days[j].wind_speed = -1
            days[j].wind_direction = None

        # pick daily forecast
        daily_forecast_list = response['daily']

        for measurement_of_day in range(len(daily_forecast_list)):
            # We just save information for today and the next 4 days
            if measurement_of_day > 4:
                break
            # read out the information
            current = daily_forecast_list[measurement_of_day]
            current_day = days.get(measurement_of_day)
            current_day.max_temp = round(current['temp']['max'])
            current_day.min_temp = round(current['temp']['min'])
            current_day_avg_weather = current['weather'][0]['main']
            if current_day_avg_weather == 'Clouds':
                current_day_avg_weather = current['weather'][0]['description']
            current_day.description = current_day_avg_weather
            if "rain" in current:
                current_day.rain_amount = current['rain']
            current_day.wind_speed = current['wind_speed']
            # defining wind direction
            current_day_wind_direction_number = current['wind_deg']
            if current_day_wind_direction_number < 23:
                current_day.wind_direction = 'N'
            elif current_day_wind_direction_number < 68:
                current_day.wind_direction = 'NO'
            elif current_day_wind_direction_number < 113:
                current_day.wind_direction = 'O'
            elif current_day_wind_direction_number < 158:
                current_day.wind_direction = 'SO'
            elif current_day_wind_direction_number < 203:
                current_day.wind_direction = 'S'
            elif current_day_wind_direction_number < 248:
                current_day.wind_direction = 'SW'
            elif current_day_wind_direction_number < 293:
                current_day.wind_direction = 'W'
            elif current_day_wind_direction_number < 348:
                current_day.wind_direction = 'NW'
            else:
                current_day.wind_direction = 'N'

        # Debugging purpose
        for j in range(5):
            print(days.get(j))
        db.commit()
    else:
        print(" City Not Found ")


if __name__ == '__main__':
    get_weather()
