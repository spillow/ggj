
import gamestate
import inputparser
import delivery

def run():
    state = gamestate.GameState()
    deliveryQueue = delivery.DeliveryQueue(state)
    while True:
        deliveryQueue.examine()
        userInput = state.prompt()
        (ok, action) = inputparser.parse(userInput)
        if ok:
            action(state)
        else:
            errMsg = action
            print errMsg
            print

