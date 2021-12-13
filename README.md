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


### Cloud Platform


### Dashboard

This are the prototype dashboard that we will be creating later using Thunkable App. It will display the temperature, humidity and heat index and also simple data like date and day.

![Dashboard](https://i.ibb.co/HF9XnbR/image3.jpg)
