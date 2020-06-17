#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <DHT_U.h>

// following depends on your pin connections
#define SOILPIN A0
#define DHTPIN 5
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char* SSID = "NETWORK-NAME";
const char* PSK = "NETWORK-PASSWORD";
const char* MQTT_BROKER = "MQTT-BROKER-IP";

WiFiClient espClient;
PubSubClient client(espClient);


void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(MQTT_BROKER, 1883);
  dht.begin();
}


// connect to the mqtt-broker
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(SSID);

  WiFi.begin(SSID, PSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


// if connection is lost try to reconnect and print the state
void reconnect() {
  while (!client.connected()) {
    Serial.print("Reconnecting...");
    if (!client.connect("ESP8266Client")) {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}
void loop() {
  float soil_V = 0;
  float temperature_V = 0;
  float humidity_V = 0;

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  delay(10000);

  // read soil moisture from sensor
  // read multiple times for a more precise value
  for(int i = 0; i < 10; i++)
  {
    soil_V = soil_V + analogRead(SOILPIN);
    delay(1);
  }
  soil_V = soil_V/10.0;

  // convert soil moisture (number in 0-1023) to percentages (0-100)
  soil_V = map(soil_V, 0, 1023, 100, 0);

  // read humdity from sensor
  humidity_V = dht.readHumidity();
  // read temperature from sensor
  temperature_V = dht.readTemperature();

  // convert all values to strings and publish them to their corresponding topic
  char buff[8];
  dtostrf(temperature_V, 6, 1, buff);
  client.publish("garden/greenhouse/temperature", buff, true);
  dtostrf(humidity_V, 6, 1, buff);
  client.publish("garden/greenhouse/humidity", buff, true);
  dtostrf(soil_V, 6, 1, buff);
  client.publish("garden/greenhouse/soil_moisture", buff, true);

}
