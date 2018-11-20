from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import requests
import json
from configparser import ConfigParser
import datetime
from os import path


class AWSInterface():

    def __init__(self):
        parser = ConfigParser()
        if path.isfile('config_files/device.conf'):
            parser.read('config_files/device.conf')

        self.host = parser.get('device', 'host')
        self.port = int(parser.get('device', 'port'))
        self.clientId = parser.get('device', 'clientId')
        self.userId = parser.get('device', 'userId')
        self.topic = parser.get('device', 'topic')
        self.rootCAPath = parser.get('device', 'rootCAPath')
        self.privateKeyPath = parser.get('device', 'privateKeyPath')
        self.certificatePath = parser.get('device', 'certificatePath')
        self.growId = parser.get('grow', 'growId')
        parser.read('plant.conf')
        self.growStartDate = None
        self.growStartDate = None
        self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
        self.myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
        self.myAWSIoTMQTTClient.configureCredentials(
            self.rootCAPath, self.privateKeyPath, self.certificatePath)
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        if(self.myAWSIoTMQTTClient.connect()):
            print("Connected successfully")
        else:
            print("Not Connected")

    def receiveData(self, topic, func):
        self.myAWSIoTMQTTClient.subscribe(topic, 1, func)

    def sendData(self, data):
        packet = self.makePacket(data)
        try:
            self.myAWSIoTMQTTClient.publish(self.topic, packet, 1)
            return True
        except Exception as e:
            raise(e)
            return False

    def makePacket(self, data):
        packet = {}
        packet['device_id'] = self.clientId
        packet['user_id'] = self.userId
        packet['time_stamp'] = str(datetime.datetime.now())
        packet['sensor_data'] = data['sensor']
        packet['grow_id'] = self.growId
        packet['time_from_start'] = str(datetime.date.today()-self.growStartDate)
        packet['actuator_data'] = data['actuator']
        iotPacket = json.dumps(packet)
        return iotPacket

    def sendCameraData(self, data):
        response = requests.post("https://aws.savetos3_api", data=data)
        return response

    def strtoDate(date):
        ''':type date: str
        :rtype: status: datetime.timedelta'''
        date = [int(x) for x in date.split('-')]
        formatted_date = datetime.date(date[0], date[1], date[2])
        return formatted_date
