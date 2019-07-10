import numpy as np
import time
import os
import cv2
from asd_rest_api.models import ScanningArea, Event
from asd_backend import settings


class EventDetector:

    def __init__(self):
        self.acceptance_threshold = 0.5
        self.proto = 'asd_drone/MobileNetSSD/MobileNetSSD_deploy.prototxt.txt'
        self.model = 'asd_drone/MobileNetSSD/MobileNetSSD_deploy.caffemodel'
        self.entities = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
        self.colors = np.random.uniform(0, 255, size=(len(self.entities), 3))
        self.net = cv2.dnn.readNetFromCaffe(self.proto, self.model)

    def analyse(self, image_path, area_id):

        image = cv2.imread(image_path)

        detections = self.compute_detections(image)

        entities = ''

        # loop over the detections
        for i in np.arange(0, self.detection_size(detections)):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = self.confidence_for(detections, i)

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > self.acceptance_threshold:
                # extract the index of the class label from the `detections`,
                # then compute the (x, y)-coordinates of the bounding box for
                # the object

                (entity, color) = self.entity_for(detections, i)
                box = self.compute_box(detections, i, image)
                entities = entities+entity+','

                self.draw_detction_in(image,
                                      box=box,
                                      entity=entity,
                                      confidence=confidence,
                                      color=color)

        if entities != '':
            self.create_event(entities=entities,
                              area_id=area_id,
                              image=image)

    def compute_detections(self, image):
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        return self.net.forward()

    def detection_size(self, detections):
        return detections.shape[2]

    def confidence_for(self, detections, index):
        return detections[0, 0, index, 2]

    def entity_for(self, detections, index):
        class_index = int(detections[0, 0, index, 1])
        return self.entities[class_index], self.colors[class_index]

    def compute_box(self, detections, index, image):
        (h, w) = image.shape[:2]
        box = detections[0, 0, index, 3:7] * np.array([w, h, w, h])
        return box.astype("int")

    def detection_label_for(self, entity, confidence):
        return "{}: {:.2f}%".format(entity, confidence * 100)

    def draw_detction_in(self, image, box, entity, confidence, color):
        # display the prediction
        label = self.detection_label_for(entity, confidence)
        print("[INFO] {}".format(label))

        (startX, startY, endX, endY) = box

        cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def create_event(self, entities, area_id, image):
        print(entities)

        image_path = self.store_image_in_media(image=image,
                                               area_id=area_id)

        if image_path is not None:
            event = Event(area_id=area_id,
                          entity=entities,
                          count=1,
                          image=image_path)

            event.save()
            print('    Saving event:', event.id, 'in area:', event.area_id, 'entity:', event.entity, 'image_path:', event.image)
        else:
            print('    COULD NOT STORE IMAGE. NO EVENT CREATD')



    def store_image_in_media(self, image, area_id):
        timestamp = str(time.time()).replace('.', '')
        image_id = str(area_id) + '_' + timestamp
        final_path = settings.BASE_DIR + settings.MEDIA_URL + str(image_id) + '.jpg'
        cv2.imwrite(final_path, img=image)

        if os.path.isfile(final_path):
            return final_path
        else:
            return None

