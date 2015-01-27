class Order:
    def __init__(self, thing, deliveryDate, action=None):
        self.thing = thing
        self.deliveryDate = deliveryDate
        self.action = action

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

        # place the objects in their appropriate places.
        if delivered:
          print
        for order in delivered:
            print "Delivery: {0}!".format(order.thing)
            container = order.thing.parent
            container.contents.append(order.thing)
            if order.action is not None:
                order.action()
        if delivered:
          print

    def AddOrder(self, order):
        self.pendingOrders.append(order)

