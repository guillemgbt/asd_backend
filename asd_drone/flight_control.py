import threading
import time
#from asd_rest_api.models import *
#import sys
#from asd_drone import constants
from djitellopy import Tello

class FlightControl:

    def __init__(self):
        self.time_constant = 0.2
        self.drone_speed = 10

    def async_start(self):
        t = threading.Thread(target=self.start, name='flight_thread')
        t.start()

    def start(self):

        print("flight control start")

        tello = Tello()

        if not tello.connect():
            print('Tello not connected.')
            return

        if not tello.set_speed(self.drone_speed):
            print("Not set speed to lowest possible")
            return

        tello.takeoff()
        time.sleep(5)

        tello.land()
        time.sleep(5)



