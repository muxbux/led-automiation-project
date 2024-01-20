#include <Arduino.h>
#include <FastLED.h>
#include <TimeLib.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "time.h"

// Define MQTT broker details
const char *mqttBroker = "test.mosquitto.org";
const int mqttPort = 1883;
const char *mqttClientId = "";
const char *mqttTopic = "leddata";

WiFiClient espClient;
PubSubClient client(espClient);

#define NUM_LEDS 60
#define DATA_PIN 22
CRGB leds[NUM_LEDS];
#define brightness 32
#define indicatorbrightness 255

CHSV maincolor = CHSV(0, 255, brightness);
CHSV secondcolor = CHSV(HUE_GREEN, 255, brightness * 2 - 1);
CHSV minutecolor = CHSV(HUE_YELLOW, 255, brightness * 2 - 1);
CHSV hourcolor = CHSV(HUE_AQUA, 255, brightness * 2 - 1);
#define indicatorcolor CHSV(0, 0, indicatorbrightness)
bool darkMode = false;

const char *ssidList[] = {"TP-Link_C64C", "Monwoefoe"};
const char *passwordList[] = {"14634604", "fdfd2767"};

const char *ntpServer = "0.be.pool.ntp.org";
const long gmtOffset_sec = 1;
const int daylightOffset_sec = 3600;

void load(int delaytime)
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CHSV(map(i, 0, 60, 0, 255), 255, brightness);
    FastLED.show();
    delay(delaytime);
  }
}

void load(int delaytime, CHSV kleur, bool display, bool marks)
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = kleur;

    if (marks && i % 5 == 0)
      leds[i] = indicatorcolor;

    if (display)
      FastLED.show();

    delay(delaytime);
  }
}

void empty(int delaytime)
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = 0x000000;
    FastLED.show();
    delay(delaytime);
  }
}

void showtime()
{
  int uurled = (hourFormat12() + 1) * 5 + (int)(minute() / 12);

  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = maincolor;
    if (i % 5 == 0)
      leds[i] = indicatorcolor;
  }
  FastLED.show();
  leds[second()] = secondcolor;
  if (second() - 1 != minute() && second() - 1 != hour() && second() % 5 == 0)
    leds[second() - 1] = maincolor;
  if (uurled != 58 && minute() != 59 && second() == 0)
    leds[59] = maincolor;

  leds[minute()] = minutecolor;
  if (minute() - 1 != second() && minute() - 1 != hour())
    leds[minute() - 1] = maincolor;
  if (uurled != 58 && minute() == 0 && second() != 59)
    leds[59] = maincolor;

  leds[uurled] = hourcolor;
  if (uurled == 0 && minute() != 59 && second() != 59)
    leds[59] = maincolor;

  FastLED.show();
}

time_t getUnixTime()
{
  Serial.println("gettingtime");
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo))
  {
    Serial.println("Failed to obtain time");
    return 0; // Return 0 or another appropriate error value
  }

  // Convert the tm struct to Unix time (seconds since 1970-01-01 00:00:00 UTC)
  time_t unixTime = mktime(&timeinfo);
  Serial.println(unixTime);
  return unixTime;
}

bool connectToWiFi()
{
  int numNetworks = sizeof(ssidList) / sizeof(ssidList[0]);

  for (int i = 0; i < numNetworks; ++i)

  {
    Serial.printf("Connecting to WiFi network: %s\n", ssidList[i]);

    WiFi.begin(ssidList[i], passwordList[i]);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10)
    {
      delay(500);
      Serial.print(".");
      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
      Serial.println("\nWiFi connected.");
      return true; // Connected successfully
    }
    else
    {
      Serial.println("\nConnection failed.");
      delay(1000);
    }
  }

  return false; // Couldn't connect to any network
}

void parseMessage(const char *message, int &mainHue, int &mode, int &hueHour, int &hueMinute, int &hueSecond, bool &mqttdarkmode)
{
  // Create a copy of the message since strtok modifies the original string
  char messageCopy[strlen(message) + 1];
  strcpy(messageCopy, message);

  // Use strtok to tokenize the message based on semicolon delimiter
  char *token = strtok(messageCopy, ";");

  // Extract individual values
  if (token != NULL)
  {
    mainHue = atoi(token);
    token = strtok(NULL, ";");
  }

  if (token != NULL)
  {
    mode = atoi(token);
    token = strtok(NULL, ";");
  }

  if (token != NULL)
  {
    hueHour = atoi(token);
    token = strtok(NULL, ";");
  }

  if (token != NULL)
  {
    hueMinute = atoi(token);
    token = strtok(NULL, ";");
  }

  if (token != NULL)
  {
    hueSecond = atoi(token);
    token = strtok(NULL, ";");
  }

  if (token != NULL)
  {
    mqttdarkmode = (strcmp(token, "True") == 0);
  }
}

void callback(char *topic, byte *payload, unsigned int length)
{
  // Handle incoming MQTT messages here
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);

  // Serial.print("Message:");
  // for (int i = 0; i < length; i++)
  // {
  //   Serial.print((char)payload[i]);
  // }
  // Serial.println();

  // Convert payload to a null-terminated string
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';

  // Parse the message and extract values
  int mainHue, mode, hueHour, hueMinute, hueSecond;
  bool mqttdarkmode;
  parseMessage(message, mainHue, mode, hueHour, hueMinute, hueSecond, mqttdarkmode);

  maincolor = CHSV(mainHue, 255, brightness);
  secondcolor = CHSV(hueSecond, 255, brightness * 2 - 1);
  minutecolor = CHSV(hueMinute, 255, brightness * 2 - 1);
  hourcolor = CHSV(hueHour, 255, brightness * 2 - 1);
  darkMode = mqttdarkmode;

  // Print the extracted values
  Serial.println("Extracted Values:");
  Serial.print("Main Hue: ");
  Serial.println(mainHue);
  Serial.print("Mode: ");
  Serial.println(mode);
  Serial.print("Hue Hour: ");
  Serial.println(hueHour);
  Serial.print("Hue Minute: ");
  Serial.println(hueMinute);
  Serial.print("Hue Second: ");
  Serial.println(hueSecond);
  Serial.print("Dark Mode: ");
  Serial.println(mqttdarkmode);
}

void connectToMQTT()
{
  // Loop until connected to MQTT broker
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(mqttClientId))
    {
      Serial.println("connected");
      // Subscribe to the MQTT topic
      client.subscribe(mqttTopic);
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup()
{

  Serial.begin(115200);

  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS); // GRB ordering is assumed
  empty(50);

  load(50);
  if (!connectToWiFi())
  {
    Serial.println("Unable to connect to any WiFi network.");
    while (1)
    {
      // Stay in this loop if unable to connect to any network
      delay(1000);
    }
  }

  empty(50);
  load(50, CHSV(HUE_RED, 255, brightness), true, true);

  // Wait for time to be synchronized
  while (time(nullptr) < 1000000000)
  {
    Serial.print(".");
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    delay(1000);
  }
  setTime(getUnixTime());

  // MQTT
  client.setServer(mqttBroker, mqttPort);
  client.setCallback(callback);
  Serial.println("MQTT connected");
}

void loop()
{
  if (!WiFi.status() == WL_CONNECTED)
  {
    while (!WiFi.status() == WL_CONNECTED)
    {
      connectToWiFi();
    }
  }

  if (!client.connected())
  {
    connectToMQTT();
  }

  // Ensure that client.loop() is called frequently
  client.loop();

  // Perform other tasks here

  if (!darkMode)
    showtime();
  else
    empty(0);

  delay(10);
}
