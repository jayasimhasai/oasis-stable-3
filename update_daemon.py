from logger import logger_variable
from configparser import ConfigParser
from aws.aws_interface import AWSInterface
import patch
import requests
import time
import os

def do_update(client, userdata, message):
	patch_location = message.payload.url
	file_name = message.payload.file_name
	parser = ConfigParser()
    parser.read('config_files/device.conf')
    user_id = parser.get('device', 'userId')

	PARAMS = { 	'user_id':user_id,
			'device_type':"aeroasis_device"
				}

	r = requests.get(url=patch_location, params=PARAMS, stream=True)
    with open("file_name", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)
    time.sleep(5)

    p = patch.fromfile("file_name")
	p.apply()

	os.system('reboot')


if __name__ == '__main__':
	AWS = AWSInterface()
	AWS.receiveData('updates',do_update)
	while True:
		time.sleep(100)