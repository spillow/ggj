
import gamestate
import inputparser
import delivery

def run():
    state = gamestate.GameState()
    deliveryQueue = delivery.DeliveryQueue(state)
    state.SetDeliveryQueue(deliveryQueue)
    while True:
        deliveryQueue.Examine()
        userInput = state.prompt()
        (ok, action) = inputparser.parse(userInput)
        if ok:
            action(state)
        else:
            errMsg = action
            print errMsg
            print

