import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime


class Greenhouse:

    def __init__(self):
        self.temperature = 'NaN'
        self.humidity = 'NaN'
        self.soil_moisture = 'NaN'


TEMPERATURE_TOPIC_NAME = 'garden/greenhouse/temperature'
HUMIDITY_TOPIC_NAME = 'garden/greenhouse/humidity'
SOIL_MOISTURE_TOPIC_NAME = 'garden/greenhouse/soil_moisture'
BROKER_ADDRESS = "localhost"
greenhouse = Greenhouse()

db = sqlite3.connect('../db_gewaechshaus.sqlite')
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS temperature(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS humidity(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS soil_moisture(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")


def on_message(client, userdata, message):
    value = str(message.payload.decode("utf-8"))
    print("message received: ", value)
    print("message topic: ", message.topic)

    date_and_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S").split(" ")
    msg_date = date_and_time[0]
    msg_time = date_and_time[1]

    if message.topic == TEMPERATURE_TOPIC_NAME:
        greenhouse.temperature = value
        cursor.execute("INSERT INTO temperature(value, date, time) VALUES(?, ?, ?);", (value, msg_date, msg_time))
    elif message.topic == HUMIDITY_TOPIC_NAME:
        greenhouse.humidity = value
    else:
        greenhouse.soil_moisture = value
        cursor.execute("INSERT INTO soil_moisture(value, date, time) VALUES(?, ?, ?);", (value, msg_date, msg_time))
    db.commit()


def on_connect(client, userdata, flags, rc):
    client.subscribe(TEMPERATURE_TOPIC_NAME)
    client.subscribe(HUMIDITY_TOPIC_NAME)
    client.subscribe(SOIL_MOISTURE_TOPIC_NAME)
    print("Connected to MQTT Broker: " + BROKER_ADDRESS)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADDRESS)
