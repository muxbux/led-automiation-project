import paho.mqtt.client as mqtt

def send_data(data, topic="leddata"):
    broker_address="test.mosquitto.org" 
    #broker_address="iot.eclipse.org" #use external broker
    client = mqtt.Client(client_id="") #create new instance
    client.connect(broker_address) #connect to broker
    client.publish(topic,data)#publish