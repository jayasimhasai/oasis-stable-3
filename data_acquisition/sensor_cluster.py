import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from atlas import *
import io         # used to create file streams
from io import open
import fcntl      # used to access I2C parameters like addresses

import string     # helps parse strings

class AtlasI2C:
	long_timeout = 1.5  
	short_timeout = .5  
	default_bus = 1     
	default_address = 100
	current_addr = default_address

	def __init__(self, address=default_address, bus=default_bus):
		
		self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
		self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

		# initializes I2C to either a user specified or default address
		self.set_i2c_address(address)

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		# The commands for I2C dev using the ioctl functions are specified in
		# the i2c-dev.h file from i2c-tools
		I2C_SLAVE = 0x703
		fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
		fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
		self.current_addr = addr

	def write(self, cmd):
		# appends the null character and sends the string over I2C
		cmd += "\00"
		self.file_write.write(cmd.encode('latin-1'))

	def read(self, num_of_bytes=31):
		# reads a specified number of bytes from I2C, then parses and displays the result
		res = self.file_read.read(num_of_bytes)         # read from the board
		if type(res[0]) is str:					# if python2 read
			response = [i for i in res if i != '\x00']
			if ord(response[0]) == 1:             # if the response isn't an error
				# change MSB to 0 for all received characters except the first and get a list of characters
				# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
				char_list = list(map(lambda x: chr(ord(x) & ~0x80), list(response[1:])))
				return "Command succeeded " + ''.join(char_list)     # convert the char list to a string and returns it
			else:
				return "Error " + str(ord(response[0]))

		else:									# if python3 read
			if res[0] == 1:
				# change MSB to 0 for all received characters except the first and get a list of characters
				# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
				char_list = list(map(lambda x: chr(x & ~0x80), list(res[1:])))
				return "Command succeeded " + ''.join(char_list)     # convert the char list to a string and returns it
			else:
				return "Error " + str(res[0])

	def query(self, string):
		# write a command to the board, wait the correct timeout, and read the response
		self.write(string)

		# the read and calibration commands require a longer timeout
		if((string.upper().startswith("R")) or
			(string.upper().startswith("CAL"))):
			time.sleep(self.long_timeout)
		elif string.upper().startswith("SLEEP"):
			return "sleep mode"
		else:
			time.sleep(self.short_timeout)

		return self.read()

	def close(self):
		self.file_read.close()
		self.file_write.close()

	def list_i2c_devices(self):
		prev_addr = self.current_addr # save the current address so we can restore it after
		i2c_devices = []
		for i in range (0,128):
			try:
				self.set_i2c_address(i)
				self.read(1)
				i2c_devices.append(i)
			except IOError:
				pass
		self.set_i2c_address(prev_addr) # restore the address we were using
		return i2c_devices


class sensorCluster:

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.trig=17
		self.echo=27
		self.ph_addr=99
		self.ec_addr=100
		GPIO.setup(self.trig,GPIO.OUT)
		GPIO.output(self.trig,0)
		GPIO.setup(self.echo,GPIO.IN)
		self.ph_sensor=AtlasI2C(address=self.ph_addr)
		self.ec_sensor=AtlasI2C(address=self.ec_addr)

	def getPh(self):
		ph_string=self.ph_sensor.query('R')
		ph_string=ph_string.replace('\x00',' ')
		ph=ph_string.split(' ')[2]
		return ph
	def getEc(self):
		ec_string=self.ec_sensor.query('R')
		ec_string=ec_string.replace('\x00',' ')
		ec=ec_string.split(' ')[2]
		ec_value= ec.split(',')[1]
		return ec_value

	def getWaterLevel(self):
		GPIO.output(self.trig,1)
		time.sleep(0.00001)
		GPIO.output(self.trig,0)
		while GPIO.input(self.echo)==0:
                                        pass
		t0=time.time()
		while GPIO.input(self.echo)==1:
                                        pass
		t1=time.time()
		dis=((t1-t0)*17000)
		#print(dis)
		return dis

	def getTempHumidity(self):
		hum,temp=Adafruit_DHT.read_retry(22,4)
		if hum is not None and temp is not None:
		    return hum,temp
		else:
			return -1,-1

	def getAllSensorData(self):
		sensors_data={}
		sensors_data["ph"]=self.getPh()
		sensors_data["ec"]=self.getEc()
		sensors_data["water_level"]=self.getWaterLevel()
		sensors_data["temp"],sensors_data["humidity"]=self.getTempHumidity()
		return sensors_data

def clear_string(string):
	for c in string:
		if(c!=b'\00'):
			return	



s=sensorCluster()
print(s.getAllSensorData())
