from serial import Serial
import json
import datetime


class SensorData:
    def __init__(self, logger):
        """
        Initialize variables and operators
        1. initialize serial port
        2. initialize GPIO pins
        """

        # cwd = os.getcwd()
        # parent_dir = os.path.dirname(cwd)
        # self.logger = logger_variable(__name__, parent_dir + '/log_files/SensorData.log')

        # open serial port
        self.interrupt_pin = 19
        self.serialOpen = Serial('/dev/ttyACM0', 115200)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.interrupt_pin, GPIO.OUT, initial=1)

        self.logger = logger

    def get_data(self):
        """
        identifier:
            sensor_data: list
            interrupt: boolean
            ack: boolean
            request: string
        :return: filter_sensor_data: dict
        """
        sensor_data = ""
        ack = False
        filter_sensor_data = {}

        # set interrupt -> False (arduino interrupt is activated on LOW)
        interrupt = False

        # receive sensor data in a dict
        while ack is False:
            try:
                GPIO.output(self.interrupt_pin, interrupt)

                sensor_data = self.receive_from_arduino()
            except ConnectionError:
                print("Connection Error")
            filter_sensor_data = self.filter_data(sensor_data)
            if filter_sensor_data['signature'] == '0xAB46CA':
                filter_sensor_data['status'] = 'OK'
                ack = True
            else:
                ack = False

        self.logger.debug('Sensor Data read')

        return filter_sensor_data

    def filter_data(self, data):
        # initialize a filter_data dictionary
        filtered_data = {}

        # split the data string into individual elements
        data_split = data.split()
        data = ['signature', 'temperature', 'humidity',
                'waterlevel', 'pH', 'turbidity', 'status', 'timestamp']

        filtered_data[data[0]] = data_split[0]
        filtered_data[data[1]] = data_split[1]
        filtered_data[data[2]] = data_split[2]
        filtered_data[data[3]] = data_split[3]
        filtered_data[data[4]] = data_split[4]
        filtered_data[data[5]] = data_split[5]
        filtered_data[data[6]] = ""
        filtered_data[data[7]] = datetime.datetime.now()

        return filtered_data

    def send_to_arduino(self, message):
        self.serialOpen.write(message)

    def receive_from_arduino(self):
        return self.serialOpen.readline()

    @staticmethod
    def convert_to_json(data):
        json_data = None
        if type(data) == dict:
            json_data = json.dumps(data)
        else:
            print("Incorrect Data Format")
        return json_data
