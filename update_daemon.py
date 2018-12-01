from configparser import ConfigParser
from aws.aws_interface import AWSInterface
import patch
import requests
import time
import os
import json

def do_update(client, userdata, message):
	file_name = "update.patch"
	URL = "https://r65hlx6e9a.execute-api.us-west-2.amazonaws.com/beta/get-system-update"
	r = requests.get(url=URL)
	data = r.json()
	file = json.loads(data['body'])['Body']['data']
	strf = ''.join(chr(i) for i in file)
	
	print(strf)
	f = open("update.patch","w")
	f.write(strf)
	f.close()
	time.sleep(5)
	print("written to file")
	p = patch.fromfile("update.patch")
	p.apply()
	print("patched applied")
	os.system('reboot')


if __name__ == '__main__':
	AWS = AWSInterface()
	AWS.receiveData('updates', do_update)
	while True:
		time.sleep(100)
