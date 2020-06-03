import sys
from src.mqtt import *
from src.gui import *


def update_weather_info():
    get_weather()
    root.after(900000, update_weather_info)


cursor.execute("CREATE TABLE IF NOT EXISTS errors(id INTEGER PRIMARY KEY, message TEXT, date_and_time TEXT);")


root.after(5000, update)
root.after(900000, update_weather_info)
while True:
    try:
        root.update()
        t.sleep(1)
        client.loop(.5)
    except Exception as e:
        print(e)
        cursor.execute("INSERT INTO errors(message, date_and_time) VALUES(?, ?);",
                       (str(e), datetime.now().strftime('%d.%m.%y %H:%M:%S')))
        db.commit()
        sys.exit()
