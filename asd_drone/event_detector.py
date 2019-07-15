import numpy as np
import time
import os
import cv2
from asd_rest_api.models import Event
from asd_backend import settings
from asd_drone.event_entity import EventEntity
from asd_drone.utils import Utils


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

    def analyse_image_in_path(self, image_path, area_id):

        image = cv2.imread(image_path)
        self.analyse_image(image, area_id)

    def analyse_image(self, image, area_id):
        detections = self.compute_detections(image)

        # NEW

        event_entities = []

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

                existing_entity = self.existing_entity_in(event_entities=event_entities,
                                                          new_element=entity)
                if existing_entity is None:
                    copy_image = image.copy()
                    box = self.compute_box(detections, i, copy_image)
                    self.draw_detction_in(copy_image,
                                          box=box,
                                          entity=entity,
                                          confidence=confidence,
                                          color=color)

                    new_event_entity = EventEntity(element=entity,
                                                   image=copy_image)

                    event_entities.append(new_event_entity)

                else:
                    entity_image = existing_entity.image
                    box = self.compute_box(detections, i, entity_image)
                    self.draw_detction_in(entity_image,
                                          box=box,
                                          entity=entity,
                                          confidence=confidence,
                                          color=color)
                    existing_entity.add_same_element()

        for event_entity in event_entities:
            Utils.printInfo(str(event_entity.count) + ' elements of ' + event_entity.element)
            self.create_event(entity=event_entity.element,
                              count=event_entity.count,
                              area_id=area_id,
                              image=event_entity.image)

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

    def existing_entity_in(self, event_entities, new_element):
        for event_entity in event_entities:
            if event_entity.is_element_from_entity(new_element):
                return event_entity
        return None

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

    def create_event(self, entity, count, area_id, image):
        image_path = self.store_image_in_media(image=image,
                                               area_id=area_id,
                                               entity=entity)

        if image_path is not None:
            event = Event(area_id=area_id,
                          entity=entity,
                          count=count,
                          image=image_path)

            event.save()
            print('-> Saving event:', event.id, 'in area:', event.area_id, 'entity:', event.entity, 'image_path:', event.image)
        else:
            print('-> COULD NOT STORE IMAGE. NO EVENT CREATED')

    def store_image_in_media(self, image, area_id, entity):
        timestamp = str(time.time()).replace('.', '')
        image_id = str(area_id) + '_' + timestamp + '_' + entity
        final_path = settings.BASE_DIR + settings.MEDIA_URL + str(image_id) + '.jpg'
        cv2.imwrite(final_path, img=image)

        if os.path.isfile(final_path):
            return '/'+image_id+'.jpg'
        else:
            return None

