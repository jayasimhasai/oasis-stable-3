import RPi.GPIO as GPIO


class ActuatorControl:
    def __init__(self, logger):
        self.interrupt = 19
        self.led_out = 21
        self.fan_out = 22
        self.pump_mixing_out = 23
        self.pump_pour_out = 24

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.interrupt, GPIO.OUT, initial=0)
        GPIO.setup(self.led_out, GPIO.OUT, initial=0)
        GPIO.setup(self.fan_out, GPIO.OUT, initial=0)
        GPIO.setup(self.pump_mixing_out, GPIO.OUT, initial=0)
        GPIO.setup(self.pump_pour_out, GPIO.OUT, initial=0)

        self.logger = logger

    def turn_light_on(self):
        light_state = 0x01
        GPIO.output(self.led_out, light_state)

    def turn_light_off(self):
        light_state = 0x00
        GPIO.output(self.led_out, light_state)

    def turn_pump_mixing_on(self):
        motor_state = 0x01
        GPIO.output(self.pump_mixing_out, motor_state)

    def turn_pump_mixing_off(self):
        motor_state = 0x00
        GPIO.output(self.pump_mixing_out, motor_state)

    def turn_pump_pour_on(self):
        motor_state = 0x01
        GPIO.output(self.pump_pour_out, motor_state)

    def turn_pump_pour_off(self):
        motor_state = 0x00
        GPIO.output(self.pump_pour_out, motor_state)

    def turn_fan_on(self):
        fan_state = 0x01
        GPIO.output(self.fan_out, fan_state)

    def turn_fan_off(self):
        fan_state = 0x00
        GPIO.output(self.fan_out, fan_state)
