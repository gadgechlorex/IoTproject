# IoTproject
A simple IoT project for Software Engineering course (SKEL413) on a weather monitoring system using M5stickC with DHT11 sensor to obtain the data

## IoT Weather Monitoring System

### Problem Statement

Weather conditions have an impact on human activity, and weather monitoring can aid in activity control. It is critical to keep an eye on and monitor the weather patterns in the area. Users have limited access to weather information such as temperature, humidity, and heat index. Users will not be notified about  heat waves, or any other weather-related emergency if they do not have access to a weather station.

Furthermore, producing weather forecasts without data is challenging. When a person uses a weather station, they can also view the information's history. The trends in the measurements can be determined by the user. The user will be able to examine patterns more effectively as a result of this.

![Case Diagram](https://i.ibb.co/mt1dCW2/image1.jpg)

### System Architecture

Here are the general overview of the system architecture of our IoT weather monitoring system. For this project we will be using the M5STICKC for the device and it will be connected to DHT11 sensor to obtain temperature, humidity, and heat index data. The device will communicate using MQTT data protocol transmission for the data transmission and it will send the data to Heroku cloud platform and finally update the data on our simple dashboard app which we will be using thunkable that we will create later.

![system architecture](https://i.ibb.co/KhHTqh1/IMAGE2.jpg)

### Sensor

#### Proposed Device: M5STICKC

![M5](https://images-na.ssl-images-amazon.com/images/I/51ykxk9ZYoL.jpg)

#### Proposed Data Transmission Protocol : MQTT

#### Code Sample

<details>
  <summary>Click to expand!</summary>

```

#include "M5stickC.h"
#include "DHT.h"
#include <WiFi.h>
extern "C" {
  #include "freertos/FreeRTOS.h"
  #include "freertos/timers.h"
}
#include <AsyncMqttClient.h>

#define WIFI_SSID "REPLACE_WITH_YOUR_SSID"
#define WIFI_PASSWORD "REPLACE_WITH_YOUR_PASSWORD"

// Raspberry Pi Mosquitto MQTT Broker
#define MQTT_HOST IPAddress(192, 168, 1, XXX)
// For a cloud MQTT broker, type the domain name
//#define MQTT_HOST "example.com"
#define MQTT_PORT 1883

// Temperature MQTT Topics
#define MQTT_PUB_TEMP "esp32/dht/temperature"
#define MQTT_PUB_HUM  "esp32/dht/humidity"
#define MQTT_PUB_HI  "esp32/dht/heatindex"

// Digital pin connected to the DHT sensor
#define DHTPIN 26  

#define DHTTYPE DHT11   // DHT 11

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// Variables to hold sensor readings
float t; //temperature
float h; //humidity
float hi; //heat index

AsyncMqttClient mqttClient;
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;

unsigned long previousMillis = 0;   // Stores last time temperature was published
const long interval = 10000;        // Interval at which to publish sensor readings

void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connectToMqtt() {
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();
}

void WiFiEvent(WiFiEvent_t event) {
  Serial.printf("[WiFi-event] event: %d\n", event);
  switch(event) {
    case SYSTEM_EVENT_STA_GOT_IP:
      Serial.println("WiFi connected");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());
      connectToMqtt();
      break;
    case SYSTEM_EVENT_STA_DISCONNECTED:
      Serial.println("WiFi lost connection");
      xTimerStop(mqttReconnectTimer, 0); // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
      xTimerStart(wifiReconnectTimer, 0);
      break;
  }
}

void onMqttConnect(bool sessionPresent) {
  Serial.println("Connected to MQTT.");
  Serial.print("Session present: ");
  Serial.println(sessionPresent);
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  Serial.println("Disconnected from MQTT.");
  if (WiFi.isConnected()) {
    xTimerStart(mqttReconnectTimer, 0);
  }
}

/*void onMqttSubscribe(uint16_t packetId, uint8_t qos) {
  Serial.println("Subscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
  Serial.print("  qos: ");
  Serial.println(qos);
}
void onMqttUnsubscribe(uint16_t packetId) {
  Serial.println("Unsubscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}*/

void onMqttPublish(uint16_t packetId) {
  Serial.print("Publish acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}

void setup() {

  M5.begin();
  M5.Lcd.setRotation(3);
  Serial.begin(9600);
  Serial.println("DHTxx test!");
  Serial.begin(115200);
  Serial.println();


  dht.begin();
  
  mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000), pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToMqtt));
  wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(2000), pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToWifi));

  WiFi.onEvent(WiFiEvent);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  //mqttClient.onSubscribe(onMqttSubscribe);
  //mqttClient.onUnsubscribe(onMqttUnsubscribe);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  // If your broker requires authentication (username and password), set them below
  //mqttClient.setCredentials("REPlACE_WITH_YOUR_USER", "REPLACE_WITH_YOUR_PASSWORD");
  connectToWifi();
}

void loop() {
  unsigned long currentMillis = millis();
  // Every X number of seconds (interval = 10 seconds) 
  // it publishes a new MQTT message
  if (currentMillis - previousMillis >= interval) {
    // Save the last time a new reading was published
    previousMillis = currentMillis;
    M5.Lcd.fillScreen(TFT_GREY);
    // New DHT sensor readings
    h = dht.readHumidity();
    // Read temperature as Celsius (the default)
    t = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    f = dht.readTemperature(true);

    // Check if any reads failed and exit early (to try again).
    if (isnan(h) || isnan(t) || isnan(f)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }

    M5.Lcd.setCursor(0, 0, 2);
    M5.Lcd.setTextColor(TFT_WHITE,TFT_BLACK);
    M5.Lcd.setTextSize(1);
    // Compute heat index
    // Must send in temp in Fahrenheit!
    float hi = dht.computeHeatIndex(f, h);
    M5.Lcd.println("");
    
    M5.Lcd.print("Humidity: ");
    M5.Lcd.println(h);
    Serial.print("Humidity: ");
    Serial.print(h);
    Serial.print(" %\t");
    M5.Lcd.setTextColor(TFT_YELLOW,TFT_BLACK);
    M5.Lcd.setTextFont(2);
    M5.Lcd.print("Temperature: ");
    M5.Lcd.println(t);
    Serial.print("Temperature: ");
    Serial.print(t);
    Serial.print(" *C ");
    Serial.print(f);
    Serial.print(" *F\t");
    M5.Lcd.setTextColor(TFT_GREEN,TFT_BLACK);
    M5.Lcd.setTextFont(2);
    M5.Lcd.print("Heat index: ");
    M5.Lcd.println(hi);
    Serial.print("Heat index: ");
    Serial.print(hi);
    Serial.println(" *F");
    }
    
    // Publish an MQTT message on topic esp32/dht/temperature
    uint16_t packetIdPub1 = mqttClient.publish(MQTT_PUB_TEMP, 1, true, String(t).c_str());                            
    Serial.printf("Publishing on topic %s at QoS 1, packetId: %i", MQTT_PUB_TEMP, packetIdPub1);
    Serial.printf("Message: %.2f \n", t);

    // Publish an MQTT message on topic esp32/dht/humidity
    uint16_t packetIdPub2 = mqttClient.publish(MQTT_PUB_HUM, 1, true, String(h).c_str());                            
    Serial.printf("Publishing on topic %s at QoS 1, packetId %i: ", MQTT_PUB_HUM, packetIdPub2);
    Serial.printf("Message: %.2f \n", h);

    // Publish an MQTT message on topic esp32/dht/heatindex
    uint16_t packetIdPub3 = mqttClient.publish(MQTT_PUB_HI, 1, true, String(hi).c_str());                            
    Serial.printf("Publishing on topic %s at QoS 1, packetId %i: ", MQTT_PUB_HI, packetIdPub3);
    Serial.printf("Message: %.2f \n", hi);
  }
}

</p>

```
</details>
  
![](https://i.ibb.co/S3n89PJ/sample.jpg)
  
### Cloud Platform


### Dashboard

This are the prototype dashboard that we will be creating later using Thunkable App. It will display the temperature, humidity and heat index and also simple data like date and day.

![Dashboard](https://i.ibb.co/HF9XnbR/image3.jpg)
