
from gamestate import GameState, Object
import inputparser
import delivery
from datetime import timedelta

from delivery import EventQueue

def run():
    state = GameState()
    queue = EventQueue(state)
    state.SetEventQueue(queue)

    def DeliverCheck(currTime, eventTime):
        Object("check", state.apartment.main.cabinet)
        queue.AddEvent(DeliverCheck, eventTime + timedelta(weeks=2))

    queue.AddEvent(DeliverCheck, state.watch.currTime + timedelta(weeks=2))
    while True:
        queue.Examine()
        userInput = state.prompt()
        (ok, action, args) = inputparser.parse(userInput)
        if ok:
            action(state, *args)
            print
        else:
            errMsg = action
            print errMsg
            print
