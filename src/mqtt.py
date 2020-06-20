import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime

TEMPERATURE_TOPIC_NAME = 'garden/greenhouse/temperature'
HUMIDITY_TOPIC_NAME = 'garden/greenhouse/humidity'
SOIL_MOISTURE_TOPIC_NAME = 'garden/greenhouse/soil_moisture'
BROKER_ADDRESS = "localhost"

# store all data in one object for most easy way of access
class Greenhouse:

    def __init__(self):
        self.temperature = 'NaN'
        self.humidity = 'NaN'
        self.soil_moisture = 'NaN'


greenhouse = Greenhouse()

# use sqlite to store data permanently
db = sqlite3.connect('../db_gewaechshaus.sqlite')
cursor = db.cursor()

# create tables
cursor.execute("CREATE TABLE IF NOT EXISTS temperature(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS humidity(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS soil_moisture(id INTEGER PRIMARY KEY, value NUMERIC, date TEXT, time TEXT);")


def on_message(client, userdata, message):

    """function executed when data is ready to be read: Reads and stores incoming data"""

    # get mqtt-message
    value = str(message.payload.decode("utf-8"))
    print("message received: ", value)
    print("message topic: ", message.topic)

    # get current date and time
    msg_date, msg_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S").split(" ")

    # check in which topic the method was published and save it
    # if topic does not match TEMPERATURE_TOPIC_NAME, HUMIDITY_TOPIC_NAME or SOIL_MOISTURE_TOPIC_NAME
    # then just ignore the message since it was probably not indicated for this script
    if message.topic == TEMPERATURE_TOPIC_NAME:
        greenhouse.temperature = value
        cursor.execute("INSERT INTO temperature(value, date, time) VALUES(?, ?, ?);", (value, msg_date, msg_time))
    elif message.topic == HUMIDITY_TOPIC_NAME:
        greenhouse.humidity = value
    elif message.topic == SOIL_MOISTURE_TOPIC_NAME:
        greenhouse.soil_moisture = value
        cursor.execute("INSERT INTO soil_moisture(value, date, time) VALUES(?, ?, ?);", (value, msg_date, msg_time))
    db.commit()


def on_connect(client, userdata, flags, rc):

    """Function executed once the client connects to the broker"""

    client.subscribe(TEMPERATURE_TOPIC_NAME)
    client.subscribe(HUMIDITY_TOPIC_NAME)
    client.subscribe(SOIL_MOISTURE_TOPIC_NAME)
    print("Connected to MQTT Broker: " + BROKER_ADDRESS)


client = mqtt.Client()
# overwrite clients function with our newly created functions
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADDRESS)
