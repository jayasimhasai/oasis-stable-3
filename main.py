from logger import logger_variable
import os
import schedule
from grow_cycle import GrowCycle
from data_acquisition.sensor_data import SensorData
from data_acquisition.camera_capture import CameraCapture
from actuator_control.actuator_control import ActuatorControl
from infrastructure.state import State
from infrastructure.critical_condition import *
from aws.aws_interface import AWSInterface
import datetime


class Main:
    def __init__(self):
        """
        :param: grow_cycle - access the config file and make schedules
                sensor_data - receive data from the arduino
                CC_queue - critical condition queue
                Data_queue - queue containing data acquired
                Image_queue - queue containing images acquired
                AWS_queue - queue containing info received from AWS
                states - to track the current states of the actuator
        """
        f = open('log_files/main.log', 'w')
        f.close()
        self.logger = logger_variable(__name__, 'log_files/main.log')

        self.states = State()
        self.grow_cycle = GrowCycle(self.states, self.logger)
        self.sensor_data = SensorData(self.logger)
        self.actuator = ActuatorControl(self.logger)
        self.camera_capture = CameraCapture(self.logger)
        self.CC_Queue = Queue()
        self.Data_Queue = Queue()
        self.Image_Queue = Queue()
        self.AWS_Queue = Queue()
        self.AWS = AWSInterface()
        self.data_log = open('log_files/data_collected.log', 'w')

    def main_function(self):

        estimated_harvest = self.grow_cycle.estimatedHarvest
        current_week = self.get_current_week()
        self.states.Current_Mode = "FOLLOW CONFIG"
        self.states.activated = False
        self.logger.debug('Grow Initiated')



        return

    def check_user_input(self, user_data):
        """
        :param user_data: data received from AWS
        :return: no return
        """
        # convert the json to dict
        data = json.loads(user_data)
        new_mode = None

        # assign the new mode to current mode in state
        if data["activity"] is "mode change":
            new_mode = data["mode"]
        self.states.Current_Mode = new_mode
        self.states.activated = False

        return

    def schedule_jobs(self):
        """
        :parameter: creating scheduling jobs
        :return:
        """
        # led scheduling
        if self.grow_cycle.ledOnDuration != 0:
            schedule.every(self.grow_cycle.ledOnInterval).day.\
                do(self.grow_cycle.light_on)

        # fan scheduling
        if self.grow_cycle.fanOnDuration != 0:
            schedule.every(self.grow_cycle.fanOnInterval).hour.\
                do(self.grow_cycle.fan_on)

        # pump_mixing scheduling
        if self.grow_cycle.pumpOnDuration != 0:
            schedule.every(self.grow_cycle.pumpOnInterval).hour.\
                do(self.grow_cycle.pump_mixing_on)

        # data acquisition and image capture scheduling
        schedule.every(self.grow_cycle.collectImageInterval).minutes.\
            do(self.get_camera_data)
        schedule.every(self.grow_cycle.collectDataInterval).minutes.\
            do(self.data_acquisition_job)

        # schedule sending data to aws
        schedule.every(self.grow_cycle.sendDataToAWSInterval).hour.\
            do(self.send_data_to_aws)

        # schedule sending images to aws S3
        # schedule.every(self.grow_cycle.sendImagesToAWSInterval).hour.\
        #     do(self.send_camera_data)
        schedule.every(self.grow_cycle.sendImagesToAWSInterval).hour. \
            do(self.logger.debug, msg='Send Images to AWS')

        return

    def data_acquisition_job(self):
        """
        :parameter: data - get sensor data
        :parameter: critical_check - get critical condition check data
        :return:
        """
        # get sensor data
        data = self.sensor_data.get_data()

        # send data for critical check
        critical_check = check_critical_condition(sensor_data=data)

        # evaluate the critical condition checklist
        # send the data to queue
        if critical_check.count("OK") < 5:
            track_critical_condition(critical_check)
            self.Data_Queue.put(data)
        else:
            self.Data_Queue.put(data)

        return

    # def interprete_item(self):
    #     return

    def get_camera_data(self):
        # get image data
        image = self.camera_capture.capture_image(frame_no=self.states.frame_no)
        self.Image_Queue.put(image)
        return

    def send_camera_data(self):
        while not self.Image_Queue.empty():
            self.AWS.sendData(self.Image_Queue.get())
        return

    def send_data_to_aws(self):
        while not self.Data_Queue.empty():
            self.write_to_file(self.Data_Queue.get())
            # self.AWS.sendData(self.Data_Queue.get())
        return

    def get_current_week(self):
        startdate = self.grow_cycle.growStartDate
        day_count = datetime.date.today() - startdate
        week_number = day_count.days / 7
        current_week = 'week'+str(week_number)
        return current_week

    def write_to_file(self, message):
        self.data_log.write(message)
        self.data_log.write('\n')
