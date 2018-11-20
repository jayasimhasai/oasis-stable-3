import subprocess


class CameraCapture:
    def __init__(self, logger):
        self.logger = logger

    def capture_image(self, frame_no):
        p = subprocess.Popen(['./raspistill.sh'], stdout=subprocess.PIPE)
        com = p.communicate()[0].decode()
        self.log('Camera Still Captured')
        return com

    def log(self, msg):
        self.logger.debug(msg)


if __name__ == '__main__':
    camera = CameraCapture()
    print(camera.capture_image().strip('\n'))

