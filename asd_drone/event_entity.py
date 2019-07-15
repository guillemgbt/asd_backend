

class EventEntity:

    def __init__(self, element, image):
        self.element = element
        self.image = image
        self.count = 1

    def add_same_element(self):
        self.count += 1

    def is_element_from_entity(self, new_element):
        return self.element == new_element
