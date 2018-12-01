from logger import *
import time
import json
import schedule
import threading
from configparser import SafeConfigParser
from queue import Queue
from grow_cycle import GrowCycle
from data_acquisition.sensor_data import SensorData
from data_acquisition.sensor_cluster import sensorCluster
from data_acquisition.camera_capture import CameraCapture
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
        self.grow_cycle = None
        #self.sensor_data = SensorData(self.logger)
        self.sensor_cluster = sensorCluster()
        self.camera_capture = CameraCapture(self.logger)
        self.CC_Queue = Queue()
        self.Data_Queue = Queue()
        self.Image_Queue = Queue()
        self.AWS_Queue = Queue()
        self.AWS = AWSInterface()
        self.data_log = open('log_files/data_collected.log', 'w')
        self.log_fn="log_files/data_collected.log"
    def main_function(self):

        self.aws_register()


        while True:
            if self.states.initiate_grow_flag == "True":
                self.grow_cycle = GrowCycle(self.states, self.logger)
                self.grow_cycle.get_growcycle_info()
                estimated_harvest = self.grow_cycle.estimatedHarvest
                current_week = self.get_current_week()

                self.logger.debug('Grow Initiated')

                while datetime.date.today() <= estimated_harvest:
                    self.states.activated = "False"

                    # start weekly jobs
                    while self.get_current_week() == current_week:

                        if self.states.Current_Mode == "FOLLOW CONFIG" and self.states.activated !="True":
                            self.grow_cycle.sched_current_week(current_week)
                            self.logger.debug('Config file scheduler created')
                            self.schedule_jobs()
                            self.states.activated = "True"
                            self.logger.debug(schedule.jobs)
                            self.logger.debug('Config file scheduler started')

                        elif self.states.Current_Mode == "WATER CHANGE" and self.states.activated !="True":
                            self.grow_cycle.sched_current_week('water_change')
                            self.logger.debug('Water Change scheduler created')
                            self.schedule_jobs()
                            self.states.activated = "True"
                            self.logger.debug(schedule.jobs)
                            self.logger.debug('Water Change scheduler started')

                        elif self.states.Current_Mode == "PH DOSING" and self.states.activated !="True":
                            self.grow_cycle.sched_current_week('ph_dosing')
                            self.logger.debug('Ph Dosing scheduler created')
                            self.schedule_jobs()
                            self.states.activated = "True"
                            self.states.ph_dosing_flag = "True"
                            self.logger.debug(schedule.jobs)
                            self.logger.debug('Ph Dosing scheduler started')

                        schedule.run_pending()
                        time.sleep(1)

                    current_week = self.get_current_week()
                    self.logger.info('New week starts')

            else:
                pass

        return


    def schedule_jobs(self):
        """
        :parameter: creating scheduling jobs
        :return:
        """
        print("Scheduling jobs")
        execute_once_time = format(datetime.datetime.now()+
                             datetime.timedelta(minutes=1),
                             '%H:%M')
        schedule.every().day.at(execute_once_time).do(self.execute_once)
        print("scheduled once...")
        # led scheduling
        if self.grow_cycle.ledOnDuration != 0:
            schedule.every(self.grow_cycle.ledOnInterval).days.\
                do(self.grow_cycle.light_on)
        self.logger.debug('LED task created')

        # fan scheduling
        if self.grow_cycle.fanOnDuration != 0:
            schedule.every(self.grow_cycle.fanOnInterval).hours.\
                do(self.grow_cycle.fan_on)
        self.logger.debug('Fan scheduler created')

        # pump_mixing scheduling
        if self.grow_cycle.pumpMixingOnDuration != 0:
            schedule.every(self.grow_cycle.pumpMixingOnInterval).hours.\
                do(self.grow_cycle.pump_mixing_on)
        self.logger.debug('Mixing pump task created')

        if self.grow_cycle.pumpPouringOnDuration != 0:
            schedule.every(self.grow_cycle.pumpPouringOnInterval).hours.\
                do(self.grow_cycle.pump_pouring_on)
        self.logger.debug('Pouring pump task created')

        # data acquisition and image capture scheduling
        schedule.every(self.grow_cycle.collectImageInterval).minutes.\
            do(self.get_camera_data)
        schedule.every(self.grow_cycle.collectDataInterval).minutes.\
            do(self.data_acquisition_job)
        self.logger.debug('data acquisition and image capture created')

        # schedule sending data to aws
        schedule.every(self.grow_cycle.sendDataToAWSInterval).minutes.\
            do(self.send_data_to_aws)
        self.logger.debug('Data sending to AWS scheduled')

        # schedule sending images to aws S3
        schedule.every(self.grow_cycle.sendImagesToAWSInterval).hours.\
            do(self.send_camera_data)
        self.logger.debug('Image sending to S3 scheduled')

        if self.states.Current_Mode == "PH DOSING":
            schedule.every(self.grow_cycle.phDosingInterval).seconds.\
                 do(self.ph_routine)
            self.logger.debug('Ph dosing routine scheduled')
        return

    def execute_once(self):
        print("Executing once..")
        if self.grow_cycle.ledOnDuration != 0:
            self.grow_cycle.light_on()
            self.logger.debug('LED task created')

        # fan scheduling
        if self.grow_cycle.fanOnDuration != 0:
            self.grow_cycle.fan_on()
            self.logger.debug('Fan scheduler created')

        # pump_mixing scheduling
        if self.grow_cycle.pumpMixingOnDuration != 0:
            self.grow_cycle.pump_mixing_on()
            self.logger.debug('Mixing pump task created')

        if self.grow_cycle.pumpPouringOnDuration != 0:
            self.grow_cycle.pump_pouring_on()
            self.logger.debug('Pouring pump task created')

        # data acquisition and image capture scheduling
        self.get_camera_data()
        self.data_acquisition_job()
        self.logger.debug('data acquisition and image capture created')

        # schedule sending data to aws
        self.send_data_to_aws()
        self.logger.debug('Data sending to AWS scheduled')

        # schedule sending images to aws S3
        self.send_camera_data()
        self.logger.debug('Image sending to S3 scheduled')

        self.logger.debug(schedule.jobs)

        return schedule.CancelJob

    def ph_routine(self):
        # get sensor data
        #data = self.sensor_data.get_data()
        data = self.sensor_cluster.getAllSensorData()
        # send data for critical check
        critical_check = check_critical_condition(sensor_data=data, states=self.states)

        if critical_check['ph'] == 'OK':
            self.states.ph_dosing_flag = "False"
        elif critical_check['ph'] == 'UP':
            self.states.ph_dosing_flag = "True"
            self.grow_cycle.ph_up_motor_on()
        elif critical_check['ph'] == 'DOWN':
            self.states.ph_dosing_flag = "True"
            self.grow_cycle.ph_down_motor_on()

        if not self.states.ph_dosing_flag:
            return schedule.CancelJob
        else:
            return

    def schedule_test_jobs(self):
        """
        :parameter: creating scheduling jobs
        :return:
        """
        # led scheduling
        if self.grow_cycle.ledOnDuration != 0:
            schedule.every(self.grow_cycle.ledOnInterval).minutes.\
                do(self.logger.info, msg='Led on')

        # fan scheduling
        if self.grow_cycle.fanOnDuration != 0:
            schedule.every(self.grow_cycle.fanOnInterval).minutes.\
                do(self.logger.info, msg='Fan On')

        schedule.every(self.grow_cycle.collectImageInterval).minutes.\
            do(self.logger.info, msg='Camera Data Received')
        schedule.every(self.grow_cycle.collectDataInterval).minutes.\
            do(self.logger.info, msg='Sensor Data Received')

        schedule.every(self.grow_cycle.sendImagesToAWSInterval).minutes. \
            do(self.logger.debug, msg='Send Images to AWS')

    def data_acquisition_job(self):
        """
        :parameter: data - get sensor data
        :parameter: critical_check - get critical condition check data
        :return:
        """
        # get sensor data
        #data = self.sensor_data.get_data()
        data = self.sensor_cluster.getAllSensorData()
        # send data for critical check
        critical_check = check_critical_condition(sensor_data=data, states=self.states)
        print(data)
        # evaluate the critical condition checklist
        # send the data to queue
        if sum( x == "OK" for x in critical_check.values() ) < 5:
            track_critical_condition(critical_check)
            self.Data_Queue.put(data)
        else:
            self.Data_Queue.put(data)

        return

    def get_camera_data(self):
        # get image data
        image = self.camera_capture.capture_image()
        self.Image_Queue.put(image)
        return

    def send_camera_data(self):
        self.logger.debug('Sending {} image packets to AWS'.format(self.Image_Queue.qsize()))
        #empty = False
        #while not empty:
            #self.AWS.sendCameraData(self.Image_Queue.get())
            #empty = self.Image_Queue.empty()
        
        return

    def send_data_to_aws(self):
        while not self.Data_Queue.empty():
            #self.write_to_file(self.Data_Queue.get())
            data = {
            "sensor":self.Data_Queue.get(),
            "actuator": {
                "led":self.states.LED_status,
                "fan":self.states.FAN_status,
                "mixing_pump":self.states.Pump_Mix_status,
                "pour_pump":self.states.Pump_Pour_status
                }
            }
            self.AWS.sendData(data)
        return

    def get_current_week(self):
        startdate = self.grow_cycle.growStartDate
        day_count = datetime.date.today() - startdate
        week_number = int(day_count.days / 7)
        current_week = 'week'+str(week_number)
        return current_week

    def write_to_file(self, message):
        fp=open(self.log_fn,'w+')
        fp.write(str(message))
        fp.close()

    def aws_register(self):
        parser = ConfigParser()
        parser.read('config_files/device.conf')
        device_id = parser.get('device', 'deviceId')
        topic = device_id+"/task"
        self.AWS.receiveData(topic, self.task_activation)

        return

    def set_mode_grow_start(self, plant_type):
        '''for now hard code plant_type
            later add functionality to
            download plant config based on plant_type'''

        ''' set some variable in config file
            read that variable and wakeup the main_function'''
        self.logger.debug('Grow Started by the user')
        schedule.clear()
        self.states.Current_Mode = "FOLLOW CONFIG"
        self.states.activated = "False"
        self.states.initiate_grow_flag = "True"
        parser =SafeConfigParser()
        parser.read("config_files/status.conf")
        parser['status']['current_mode'] = "FOLLOW CONFIG"
        parser['status']['activated'] = "False"
        parser['status']['initiate_grow_flag'] = "True"
        with open('config_files/status.conf','w') as configfile:
            parser.write(configfile)
        parser =SafeConfigParser()
        parser.read("config_files/plant.conf")
        plantCycleDuration = parser.get('PlantInfo', 'plantCycle')
        parser['PlantInfo']['plantingDate'] = str(datetime.date.today())
        parser['PlantInfo']['estimatedHarvest'] = str(datetime.date.today() + datetime.timedelta(weeks=int(plantCycleDuration)))
        with open('config_files/plant.conf','w') as configfile:
            parser.write(configfile)
        return

    def set_mode_grow_end(self):
        ''' clear the schedular
            clear varibles in config file
            set mode to sleep state or something
            which waits for start grow'''
        self.logger.debug('Grow Ends')
        schedule.clear()
        self.states.Current_Mode = "GROW END"
        self.states.activated = "False"
        self.states.initiate_grow_flag = "False"
        parser =SafeConfigParser()
        parser.read("config_files/status.conf")
        parser['status']['current_mode'] = "GROW END"
        parser['status']['activated'] = "False"
        parser['status']['initiate_grow_flag'] = "False"
        with open('config_files/status.conf','w') as configfile:
        	parser.write(configfile)
        return

    def set_mode_water_change(self, param):
        '''change mode to water change mode
            if param is start
            if param is end set the mode to grow'''
        self.logger.debug('Water Change initiated by the user')
        schedule.clear()
        if param == 'start':
            self.states.Current_Mode = "WATER CHANGE"
            self.states.activated = "False"
            parser =SafeConfigParser()
            parser.read("config_files/status.conf")
            parser['status']['current_mode'] = "WATER CHANGE"
            parser['status']['activated'] = "False"
            with open('config_files/status.conf','w') as configfile:
            	parser.write(configfile)
        elif param == 'end':
            self.states.Current_Mode = "FOLLOW CONFIG"
            self.states.activated = "False"
            parser =SafeConfigParser()
            parser.read("config_files/status.conf")
            parser['status']['current_mode'] = "FOLLOW CONFIG"
            parser['status']['activated'] = "False"
            with open('config_files/status.conf','w') as configfile:
            	parser.write(configfile)
        else:
            self.logger.debug('Wrong Water change input')
        return

    def set_mode_ph_change(self, param):
        '''change mode to ph change mode
            if param is start
            else set it to grow mode'''

        schedule.clear()
        self.logger.debug('Ph dosing initiated by the user')
        if param == 'start':
            self.states.Current_Mode = "PH DOSING"
            self.states.activated = "False"
            parser =SafeConfigParser()
            parser.read("config_files/status.conf")
            parser['status']['current_mode'] = "PH DOSING"
            parser['status']['activated'] = "False"
            with open('config_files/status.conf','w') as configfile:
            	parser.write(configfile)
        elif param == 'end':
            self.states.Current_Mode = "FOLLOW CONFIG"
            self.states.activated = "False"
            parser =SafeConfigParser()
            parser.read("config_files/status.conf")
            parser['Status']['current_mode'] = "FOLLOW CONFIG"
            parser['Status']['activated'] = "False"
            with open('config_files/status.conf','w') as configfile:
            	parser.write(configfile)
        else:
            self.logger.debug('Wrong ph dosing input')
        return

    def task_activation(self, client, userdata, message):

        data = json.loads(message.payload.decode())

        task = data['task']

        self.logger.debug('user activated task %s', task)
        if task == "grow-start":
            plant_type = data['plant_type']
            self.set_mode_grow_start(plant_type)

        elif task == "grow-end":
            self.set_mode_grow_end()

        elif task == "water-change-start":
            self.set_mode_water_change("start")

        elif task == "water-change-end":
            self.set_mode_water_change("end")

        elif task == "ph-dosing-start":
            self.set_mode_ph_change("start")

        elif task == "ph-dosing-end":
            self.set_mode_ph_change("end")

        else:
            self.logger.error('unknown task %s', task)


if __name__ == '__main__':
    main_soft = Main()
    main_soft.main_function()
