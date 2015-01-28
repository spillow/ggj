
from gamestate import GameState, Object
import inputparser
import delivery
from datetime import timedelta

class GovChecks:
    def __init__(self, lastTime):
        self.lastTime = lastTime

    def CheckChecks(self, state, queue, currTime):
        if currTime >= self.lastTime + timedelta(weeks=2):
            order = delivery.Order(
                Object("check", state.apartment.main.cabinet),
                currTime + timedelta(weeks=2))
            queue.AddOrder(order)
            self.lastTime = currTime

def run():
    state = GameState()
    deliveryQueue = delivery.DeliveryQueue(state)
    state.SetDeliveryQueue(deliveryQueue)
    checks = GovChecks(state.watch.currTime - timedelta(weeks=2))
    while True:
        checks.CheckChecks(state, deliveryQueue, state.watch.currTime)
        deliveryQueue.Examine()
        userInput = state.prompt()
        (ok, action, args) = inputparser.parse(userInput)
        if ok:
            action(state, *args)
            print
        else:
            errMsg = action
            print errMsg
            print

