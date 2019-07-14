import threading
import time
from asd_rest_api.models import *
from asd_drone import constants
from djitellopy import Tello
from asd_drone.utils import Utils
from asd_drone.event_detector import EventDetector
from asd_drone.VideoGet import VideoGet


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

        flight_state = self.get_flight_state()

        if flight_state is None:
            Utils.printError('No flight state')
            self.set_state_to(new_state=constants.STATE_ERROR)
            return

        area = self.get_area_in(flight_state=flight_state)

        if area is None:
            Utils.printError('No flight area')
            self.set_state_to(new_state=constants.STATE_ERROR)
            return

        if not self.set_up_drone():
            self.set_state_to(new_state=constants.STATE_ERROR)
            return

        stream = VideoGet(drone=self.drone)
        stream.start()

        self.drone.takeoff()
        time.sleep(5)

        self.drone.move_up(30)
        time.sleep(5)

        should_stop = False
        self.set_state_to(new_state=constants.STATE_SCANNING)
        while not should_stop:
            image = stream.frame
            detector = EventDetector()
            detector.analyse_image(image, area_id=area.id)

            flight_state = self.get_flight_state()
            should_stop = flight_state.state == constants.STATE_STOPPING

            self.drone.rotate_clockwise(90)
            time.sleep(5)

        stream.stop()
        self.drone.land()
        self.set_state_to(constants.STATE_LANDED)

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

    def set_state_to(self, new_state):
        flight_state = self.get_flight_state()
        flight_state.state = new_state
        flight_state.save(update_fields=['state'])
        print('setting flight state to:', flight_state.state)




