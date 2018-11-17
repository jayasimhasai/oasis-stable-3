from logger import logger_variable
import subprocess
import os


class CameraCapture:
    def __init__(self):
        cwd = os.getcwd()
        parent_dir = os.path.dirname(cwd)
        self.logger = logger_variable(__name__, parent_dir+'/log_files/CameraCapture.log')

    def capture_image(self):
        p = subprocess.Popen(['./raspistill.sh'], stdout=subprocess.PIPE)
        com = p.communicate()[0].decode()
        self.log('Camera Still Captured')
        return com

    def log(self, msg):
        self.logger.debug(msg)


if __name__ == '__main__':
    camera = CameraCapture()
    print(camera.capture_image().strip('\n'))

