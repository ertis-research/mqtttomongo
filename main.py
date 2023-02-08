
from paho.mqtt import client as mqtt_client
from pymongo import MongoClient
import json
import csv
import os
import datetime
###################### MQTT broker conection ################################
broker = os.environ['MOSQUITTO_BROKER']+"-mosquitto"
port = int(os.environ['MQTTPORT'])
#port = 30510
topic = "#"
client_id = 'mqttToMongo'
toInsert = False
print(broker)
print(port)
print(type(port))

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(topic)
            client.on_message = on_message
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(client, userdata, msg):
        jsonMessage = msg.payload.decode()
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        diccToInsert = json.loads(jsonMessage)
        diccToInsert['topic_id'] = msg.topic
        diccToInsert['createdAt'] = datetime.datetime.utcnow()
        print(jsonMessage)

        print("Inserting message on MongoDB")
        try:
            db = clientMongo["dtdatastorage"]
            data = db["timeseries"]
            result = data.insert_one(diccToInsert)
            print(f"Inserted message with ID: {result.inserted_id}")
            if toInsert == True:
                print("Inserting previous failed messages")
                insertFailedMessagesIntoMongoDB()
        except Exception as e:
            print(e)
            print("Saving message for later insertion")
            messageToSave = json.loads(jsonMessage)
            messageToSave['topic_id'] = msg.topic
            saveFailedMessage(json.dumps(messageToSave))

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_forever()
    return client

    

####################### MongoDB conection ########################################
clientMongo = MongoClient(host = os.environ['MOSQUITTO_BROKER']+"-mongodb", port=27017)

def insertFailedMessagesIntoMongoDB():
    print("Saving previous messages")
    global toInsert
    toInsert = False
    with open("failedMessages.txt", "r") as f:
        messages = f.readlines()
        for message in messages:
            diccToInsert = json.loads(message)
            diccToInsert['createdAt'] = datetime.datetime.utcnow()
            db = clientMongo["dtdatastorage"]
            data = db["timeseries"]
            result = data.insert_one(diccToInsert)
            print(f"Inserted message with ID: {result.inserted_id}")
        print("Inserted {} messages on MongoDB".format(len(messages)))

    if os.path.exists("failedMessages.txt"):
        os.remove("failedMessages.txt")


def saveFailedMessage(failedMessage):
    global toInsert
    toInsert = True
    with open("failedMessages.txt", "a") as f:
        f.write(failedMessage)
        f.write("\n")

def run():
    client = connect_mqtt()
    #subscribe(client)
if __name__ == '__main__':
    run()