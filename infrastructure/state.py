
class State:
    def __init__(self):
        self.LED_status = False
        self.FAN_status = False
        self.Pump_Mix_status = False
        self.Pump_Pour_status = False
        self.frame_no = 0
        self.Current_Mode = None
        self.activated = None
        self.active_cc_tracker = False
        self.tempUL = 0.0
        self.tempLL = 0.0
        self.humidityUL = 0.0
        self.humidityLL = 0.0
        self.phUL = 0.0
        self.phLL = 0.0
        self.ecUL = 0.0
        self.ecLL = 0.0
        self.waterlevelUL = 0.0
        self.waterlevelLL = 0.0