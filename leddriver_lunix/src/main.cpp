#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define red GPIO_NUM_19
#define green GPIO_NUM_18
#define blue GPIO_NUM_16
#define white GPIO_NUM_17

// Define MQTT broker details
const char *mqttBroker = "test.mosquitto.org";
const int mqttPort = 1883;
const char *mqttClientId = "";
const char *mqttTopic = "leddata";

WiFiClient espClient;
PubSubClient client(espClient);

const char *ssidList[] = {"TP-Link_C64C", "Monwoefoe"};
const char *passwordList[] = {"14634604", "fdfd2767"};

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

void setRGBColor(int hue)
{
  // Convert HSV to RGB
  int sector = hue / 60;
  int remainder = (hue % 60) * 255 / 60;

  int r, g, b;

  switch (sector)
  {
  case 0:
    r = 255;
    g = remainder;
    b = 0;
    break;
  case 1:
    r = 255 - remainder;
    g = 255;
    b = 0;
    break;
  case 2:
    r = 0;
    g = 255;
    b = remainder;
    break;
  case 3:
    r = 0;
    g = 255 - remainder;
    b = 255;
    break;
  case 4:
    r = remainder;
    g = 0;
    b = 255;
    break;
  case 5:
    r = 255;
    g = 0;
    b = 255 - remainder;
    break;
  default:
    r = 0;
    g = 0;
    b = 0;
    break;
  }

  // Write RGB values to the corresponding PWM pins
  analogWrite(red, r);
  analogWrite(green, g);
  analogWrite(blue, b);
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

  
  // Print the extracted values
  Serial.println("Extracted Values:");
  Serial.print("Main Hue: ");
  Serial.println(mainHue);
  Serial.print("Mode: ");
  Serial.println(mode);
  Serial.print("Dark Mode: ");
  Serial.println(mqttdarkmode);
  if(!mqttdarkmode)setRGBColor(mainHue);
  else{
      analogWrite(red, 0);
      analogWrite(green, 0);
      analogWrite(blue, 0);
  }
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



void setup() {
  Serial.begin(115200);

  if (!connectToWiFi())
  {
    Serial.println("Unable to connect to any WiFi network.");
    while (1)
    {
      // Stay in this loop if unable to connect to any network
      delay(1000);
    }
  }
  client.setServer(mqttBroker, mqttPort);
  client.setCallback(callback);
  Serial.println("MQTT connected");
}

void loop() {
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
}
