from datetime import *
import requests
from src.mqtt import cursor, db
from Credentials.credentials import *
from collections import OrderedDict

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

    """structure to save data for each day"""

    def __init__(self):
        self.date = None
        self.weekday = None
        self.max_temp = -50
        self.min_temp = 9999
        self.description = None
        self.rain_amount = 0
        self.snow_amount = 0
        self.wind_speed = -1
        self.wind_direction = None
        self.temperatures = OrderedDict()
        self.hourly_descriptions = OrderedDict()
        self.sunset = 0

    def __str__(self):

        """just for debugging purposes. Prints out every var to console"""

        ret = self.weekday + ', ' + self.date + ': ' + str(self.max_temp) + '°C/' + str(self.min_temp) + '°C, ' + \
              str(self.description) + '\nRain: ' + str(self.rain_amount) + \
              '\nSnow: ' + str(self.snow_amount) + '\nWind: ' + str(self.wind_speed) + ' ' + self.wind_direction + \
              '\nSunset at: ' + self.sunset + '\n'

        if len(self.hourly_descriptions) > 0:
            ret = ret + 'hourly_forecast:\n'
            keys = list(self.temperatures.keys())
            values_temperature = list(self.temperatures.values())
            values_hourly_descriptions = list(self.hourly_descriptions.values())
            for t in range(len(self.temperatures)):
                ret = ret + str(keys[t]) + ': ' + str(values_temperature[t]) + ' °C, ' + \
                      str(values_hourly_descriptions[t]) + '\n'
        return ret


class Today(Day):

    """Specialized Day. Saves additional data concerning the current day"""

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
    # make request to url
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
            days[j].snow_amount = 0
            days[j].wind_speed = -1
            days[j].wind_direction = None
            days[j].temperatures = OrderedDict()
            days[j].hourly_descriptions = OrderedDict()
            days[j].sunset = 0

        # daily forecast
        daily_forecast_list = response['daily']
        dates_as_timestamps = []

        for measurement_of_day in range(len(daily_forecast_list)):
            # We just save information for today and the next 4 days
            if measurement_of_day > 4:
                break
            # read data out of json file
            current = daily_forecast_list[measurement_of_day]
            current_day = days.get(measurement_of_day)
            current_day.max_temp = round(current['temp']['max'])
            current_day.min_temp = round(current['temp']['min'])
            current_sunset = datetime.fromtimestamp(current['sunset'])
            current_day.sunset = current_sunset.strftime('%H:%M')
            current_day_avg_weather = current['weather'][0]['main']

            # Clouds would be too general. We want it more precise
            if current_day_avg_weather == 'Clouds':
                current_day_avg_weather = current['weather'][0]['description']
            current_day.description = current_day_avg_weather

            if "rain" in current:
                current_day.rain_amount = current['rain']
            if "snow" in current:
                current_day.snow_amount = current['snow']
            current_day.wind_speed = round(current['wind_speed'] * 3.6, 1)

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

            dates_as_timestamps.append(current['dt'])

        # Hourly forecast
        hourly_forecast_list = response['hourly']

        for hour in range(len(hourly_forecast_list)):
            # for every entry
            for d in range(len(dates_as_timestamps)):
                if hourly_forecast_list[hour]['dt'] < dates_as_timestamps[d] - 48001:
                    # the entry is of which day?
                    hour_time = datetime.fromtimestamp(hourly_forecast_list[hour]['dt'])
                    hour_time_as_string = hour_time.strftime('%H') + 'Uhr'
                    days[d - 1].temperatures[hour_time_as_string] = round(hourly_forecast_list[hour]['temp'])
                    hourly_weather = hourly_forecast_list[hour]['weather'][0]['main']

                    if hourly_weather == 'Clouds':
                        hourly_weather = hourly_forecast_list[hour]['weather'][0]['description']
                    days[d - 1].hourly_descriptions[hour_time_as_string] = hourly_weather
                    break

        # Debugging purpose
        for j in range(5):
            print(days.get(j))
    else:
        print(" City Not Found ")


if __name__ == '__main__':
    get_weather()
