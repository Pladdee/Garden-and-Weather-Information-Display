import sys
from src.mqtt import *
from src.gui import *


# get new weather data every 15minutes (60*15*1000 milliseconds)
def update_weather_info():
    get_weather()
    root.after(900000, update_weather_info)


root.update_view()
root.after(900000, update_weather_info)
# update and listen to possible new mqtt-data
# loop forever
while True:
    try:
        root.update()
        t.sleep(1)
        client.loop(.5)
    except Exception as e:
        print(e)
        sys.exit()
