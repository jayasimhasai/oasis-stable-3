from configparser import ConfigParser
from infrastructure.state import State
from logger import logger_variable
import datetime
from os import path
import schedule


class GrowCycle:
    def __init__(self, states, logger_received):
        self.parser = ConfigParser()
        self.logger = logger_received
        if path.isfile("config_files/plant.conf"):
            self.logger.debug("config_file present")
            self.parser.read('config_files/plant.conf')
        self.plantCycleDuration = self.parser.get('PlantInfo', 'plantCycle')
        self.growStartDate = datetime.datetime.now()
        self.estimatedHarvest = datetime.datetime.now() + datetime.timedelta(weeks=int(self.plantCycleDuration))
        self.tempUL = None
        self.tempLL = None
        self.humidityUL = None
        self.humidityLL = None
        self.phUL = None
        self.phLL = None
        self.ecUL = None
        self.ecLL = None
        self.waterlevelUL = None
        self.waterlevelLL = None
        self.ledOnDuration = None
        self.ledOnInterval = None
        self.fanOnDuration = None
        self.fanOnInterval = None
        self.pumpMixingOnDuration = None
        self.pumpMixingOnInterval = None
        self.pumpPouringOnDuration = None
        self.pumpPouringOnInterval = None
        self.collectDataDuration = None
        self.collectCameraInterval = None
        self.collectCameraDuration = None
        self.sendDataToAWSInterval = None
        self.sendImagesToAWSInterval = None
        self.collectDataInterval = 30
        self.collectImageInterval = 60
        # self.Actuator = ActuatorControl()
        self.states = states

    def sched_current_week(self, currentWeek):

        # | add try catch later |

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
        self.pumpMixingOnDuration = int(self.parser.get(currentWeek,
                                                        'pumpMixingOnDuration'))
        self.pumpMixingOnInterval = int(self.parser.get(currentWeek,
                                                        'pumpMixingOnInterval'))
        self.pumpPouringOnDuration = int(self.parser.get(currentWeek,
                                                         'pumpPouringOnDuration'))
        self.pumpPouringOnInterval = int(self.parser.get(currentWeek,
                                                         'pumpPouringOnInterval'))
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

    # | add try catch to all the actuator functions |

    def light_on(self):
        self.Actuator.turn_light_on()
        self.logger.debug('Led switched ON')
        self.states.LED_status = True
        lightOffTime = format(datetime.datetime.now() +
                              datetime.timedelta(hours=self.ledOnDuration),
                              '%H:%M:%S')
        schedule.every().day.at(lightOffTime).do(self.lightOff)

    def light_off(self):
        self.Actuator.turn_light_off()
        self.logger.debug('Led Switch Off')
        self.states.LED_status = False
        return schedule.CancelJob

    def fan_on(self):
        self.Actuator.turn_fan_on()
        self.logger.debug('Fan switched ON')
        self.states.FAN_status = True
        fanOffTime = format(datetime.datetime.now() +
                            datetime.timedelta(minutes=self.fanOnDuration),
                            '%H:%M:%S')
        schedule.every().day.at(fanOffTime).do(self.fanOff)

    def fan_off(self):
        self.Actuator.turn_fan_off()
        self.logger.debug('Fan switched Off')
        self.states.FAN_status = False
        return schedule.CancelJob

    def pump_mixing_on(self):
        self.Actuator.turn_pump_mixing_on()
        self.logger.debug('Mixing Pump switched ON')
        self.states.Pump_Mix_status = True
        pumpOffTime = format(datetime.datetime.now() +
                             datetime.timedelta(minutes=self.pumpMixingOnDuration),
                             '%H:%M:%S')
        schedule.every().day.at(pumpOffTime).do(self.pumpMixingOff)

    def pump_mixing_off(self):
        self.Actuator.turn_pump_mixing_off()
        self.logger.debug('Mixing Pump switched OFF')
        self.states.Pump_Mix_status = False
        return schedule.CancelJob

    def pump_pouring_on(self):
        self.Actuator.turn_pump_pour_on()
        self.logger.debug('Pouring Pump switched ON')
        self.states.Pump_Mix_status = True
        pumpOffTime = format(datetime.datetime.now() +
                             datetime.timedelta(minutes=self.pumpPouringOnDuration),
                             '%H:%M:%S')
        schedule.every().day.at(pumpOffTime).do(self.pumpOff)

    def pump_pouring_off(self):
        self.Actuator.turn_pump_pour_off()
        self.logger.debug('Pouring Pump switched OFF')
        self.states.Pump_Mix_status = False
        return schedule.CancelJob

    def get_growcycle_info(self):
        if path.isfile("config_files/plant.conf"):
            self.logger.debug('Config File Found')
            self.parser.read('config_files/plant.conf')
            self.plantCycleDuration = self.parser.get('PlantInfo', 'plantCycle')
            self.growStartDate = datetime.datetime.now()
            self.estimatedHarvest = datetime.datetime.now() + datetime.timedelta(weeks=int(self.plantCycleDuration))
            self.logger.debug('Config File Read')
        else:
            self.logger.error('Config File Not Found')


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
