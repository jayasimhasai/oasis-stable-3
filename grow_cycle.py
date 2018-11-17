from configparser import ConfigParser
from infrastructure.state import State
from logger import logger_variable
import datetime
from os import path
import schedule


class GrowCycle:
    def __init__(self, states, logger_received):
        self.parser = ConfigParser()
        if path.isfile("config_files/plant.conf"):
            print("config_file present")
        self.parser.read('config_files/plant.conf')
        self.plantCycleDuration = self.parser.get('PlantInfo', 'plantCycle')
        self.growStartDate = datetime.datetime.now()
        self.estimatedHarvest = datetime.datetime.now() + datetime.timedelta(weeks=int(self.plantCycleDuration))
        self.ledOnDuration = None
        self.ledOnInterval = None
        self.fanOnDuration = None
        self.fanOnInterval = None
        self.pumpOnDuration = None
        self.pumpOnInterval = None
        self.collectDataInterval = None
        self.collectImageInterval = None
        # self.Actuator = ActuatorControl()
        self.states = states
        self.logger = logger_received

    def schedCurrentWeek(self, currentWeek):
        # parser = ConfigParser()
        self.parser.read('config_files/plant.conf')
        # get plant critical data
        self.tempUL = int(self.parser.get(currentWeek, 'tempUL'))
        self.tempLL = int(self.parser.get(currentWeek, 'tempLL'))
        self.humidityUL = int(self.parser.get(currentWeek,
                                              'humidityUL'))
        self.humidityLL = int(self.parser.get(currentWeek,
                                              'humidityLL'))
        self.phUL = float(self.parser.get(currentWeek, 'phUL'))
        self.phLL = float(self.parser.get(currentWeek, 'phLL'))
        self.ecUL = float(self.parser.get(currentWeek, 'ecUL'))
        self.ecLL = float(self.parser.get(currentWeek, 'ecLL'))
        self.waterlevelUL = int(self.parser.get(currentWeek,
                                                'waterlevelUL'))
        self.waterlevelLL = int(self.parser.get(currentWeek,
                                                'waterlevelLL'))
        self.ledOnDuration = float(self.parser.get(currentWeek,
                                                   'ledOnDuration'))
        self.ledOnInterval = float(self.parser.get(currentWeek,
                                                   'ledOnInterval'))
        self.fanOnDuration = float(self.parser.get(currentWeek,
                                                   'fanOnDuration'))
        self.fanOnInterval = float(self.parser.get(currentWeek,
                                                   'fanOnInterval'))
        self.pumpOnDuration = int(self.parser.get(currentWeek,
                                                  'pumpOnDuration'))
        self.pumpOnInterval = int(self.parser.get(currentWeek,
                                                  'pumpOnInterval'))
        self.collectDataInterval = int(self.parser.get(currentWeek,
                                                       'collectDataInterval'))
        self.collectDataDuration = int(self.parser.get(currentWeek,
                                                       'collectDataDuration'))
        self.collectCameraInterval = int(self.parser.get(currentWeek,
                                                         'collectCameraInterval'))
        self.collectCameraDuration = int(self.parser.get(currentWeek,
                                                         'collectCameraDuration'))
        self.sendDataToAWSInterval = float(self.parser.get(currentWeek,
                                                           'sendDataInterval'))
        self.sendImagesToAWSInterval = float(self.parser.get(currentWeek,
                                                             'sendImagesInterval'))

        self.logger.debug('Read config file')

        self.initialize_states()

    def initialize_states(self):
        """
        Initialize the global states with the plant.conf
        :return:No return
        """
        self.states.tempLL = self.tempLL
        self.states.tempUL = self.tempUL
        self.states.humidityUL = self.humidityUL
        self.states.humidityLL = self.humidityLL
        self.states.phUL = self.phUL
        self.states.phLL = self.phLL
        self.states.ecUL = self.ecUL
        self.states.ecLL = self.ecLL
        self.states.waterlevelUL = self.waterlevelUL
        self.states.waterlevelLL = self.waterlevelLL

        self.logger.debug('Global states declared')


if __name__ == '__main__':
    statesv = State()
    f = open('main8.log', 'w')
    f.close()
    logger = logger_variable(__name__, 'main8.log')
    grow = GrowCycle(statesv, logger)
    grow.schedCurrentWeek('week0')
    print(grow.tempUL)
    schedule.every(grow.ledOnInterval).minutes.do(logger.info, msg='Led on')
    while True:
        schedule.run_pending()