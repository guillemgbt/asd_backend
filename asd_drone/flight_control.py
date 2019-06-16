import threading
import time
from asd_rest_api.models import *
import sys
from asd_drone import constants


class FlightControl:

    def __init__(self):
        self.time_constant = 0.2

    def async_start(self):
        t = threading.Thread(target=self.start, name='flight_thread')
        t.start()

    def start(self):

        print("flight control start")

