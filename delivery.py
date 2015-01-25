class Order:
    def __init__(self, thing, deliveryDate):
        self.thing = thing
        self.deliveryDate = deliveryDate

class DeliveryQueue:
    def __init__(self, gamestate):
        self.gamestate = gamestate

    def examine(self):
        pass

