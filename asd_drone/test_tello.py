from djitellopy import Tello
import cv2
import numpy as np
import time


class TestTello:

    def execute(self):

        tello = Tello()

        if not tello.connect():
            print("Tello not connected")
            return

        if not tello.set_speed(10):
            print("Not set speed to lowest possible")
            return
        # In case streaming is on. This happens when we quit this program without the escape key.
        if not tello.streamoff():
            print("Could not stop video stream")
            return
        if not tello.streamon():
            print("Could not start video stream")
            return

        frame_read = tello.get_frame_read()

        time.sleep(2)

        image = frame_read.frame

        print(image)

        tello.end()

        # if frame_read.stopped:
        #     frame_read.stop()
