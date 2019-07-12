import threading
import time
from asd_rest_api.models import *
from asd_drone import constants
from djitellopy import Tello
from asd_drone.utils import Utils
from asd_drone.event_detector import EventDetector


class FlightControl:

    def __init__(self):
        self.time_constant = 0.2
        self.drone_speed = 10
        self.drone = None

    def async_start(self):
        t = threading.Thread(target=self.start, name='flight_thread')
        t.start()

    def start(self):

        Utils.printInfo('Flight control start')

        state = self.get_flight_state()

        if state is None:
            Utils.printError('No flight state')
            return

        area = self.get_area_in(flight_state=state)

        if area is None:
            Utils.printError('No flight area')
            return

        if not self.set_up_drone():
            return

        # self.drone.takeoff()
        # time.sleep(5)
        #
        # self.drone.land()
        # time.sleep(5)

        frame_read = self.drone.get_frame_read()

        time.sleep(2)
        image = frame_read.frame

        detector = EventDetector()
        detector.analyse_image(image, area_id=area.id)

        frame_read.stop()
        self.drone.end()

    def get_flight_state(self):
        return FlightState.objects.first()

    def get_area_in(self, flight_state):
        return ScanningArea.objects.get(pk=flight_state.area_id)

    def set_up_drone(self):

        self.drone = Tello()

        if not self.drone.connect():
            Utils.printError('Tello not connected')
            return False

        if not self.drone.set_speed(self.drone_speed):
            Utils.printError('Not set speed to lowest possible')
            return False

        # In case streaming is on.
        if not self.drone.streamoff():
            Utils.printError('Could not stop video stream')
            return False

        if not self.drone.streamon():
            Utils.printError('Could not start video stream')
            return False

        return True




