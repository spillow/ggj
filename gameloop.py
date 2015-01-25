
import gamestate
import inputparser
import delivery
from datetime import timedelta

class GovChecks:
    def __init__(self, lastTime):
        self.lastTime = lastTime

    def CheckChecks(self, state, queue, currTime):
        if currTime >= self.lastTime + timedelta(weeks=2):
            order = delivery.Order(
                "check",
                currTime + timedelta(weeks=2),
                "cabinet")
            queue.AddOrder(order)
            self.lastTime = currTime

def run():
    state = gamestate.GameState()
    deliveryQueue = delivery.DeliveryQueue(state)
    state.SetDeliveryQueue(deliveryQueue)
    checks = GovChecks(state.currTime - timedelta(weeks=2))
    while True:
        checks.CheckChecks(state, deliveryQueue, state.currTime)
        deliveryQueue.Examine()
        userInput = state.prompt()
        (ok, action) = inputparser.parse(userInput)
        if ok:
            action(state)
        else:
            errMsg = action
            print errMsg
            print

