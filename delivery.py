class Order:
    def __init__(self, thing, deliveryDate, whereToPut):
        self.thing = thing
        self.deliveryDate = deliveryDate
        self.whereToPut = whereToPut

class DeliveryQueue:
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.pendingOrders = []

    def Examine(self):
        # Get items that have hit the delivery time.
        delivered = [x for x in self.pendingOrders if
            self.gamestate.currTime >= x.deliveryDate]
        remaining = [x for x in self.pendingOrders if
            self.gamestate.currTime < x.deliveryDate]

        self.pendingOrders = remaining

        if len(delivered) != 0:
            print "You have new deliveries!"

        # place the objects in their appropriate places.
        for order in delivered:
            container = self.gamestate.GetRoomObjects(order.whereToPut)[0]
            container.contents.append(self.gamestate.MakeRoomObject(order.thing))

    def AddOrder(self, order):
        self.pendingOrders.append(order)

