from .gamestate import GameState, Object
from .io_interface import IOInterface, ConsoleIO
from . import inputparser
from . import delivery
from datetime import timedelta
import datetime
from typing import Optional

from .delivery import EventQueue


def run(io: Optional[IOInterface] = None) -> None:
    if io is None:
        io = ConsoleIO()
    
    state = GameState(io)
    queue = EventQueue(state)
    state.SetEventQueue(queue)

    def DeliverCheck(currTime: datetime.datetime, eventTime: datetime.datetime) -> None:
        io.output("Government check in the mail!")
        Object("check", state.apartment.main.cabinet)
        queue.AddEvent(DeliverCheck, eventTime + timedelta(weeks=2))

    queue.AddEvent(DeliverCheck, state.watch.curr_time + timedelta(weeks=2))
    state.IntroPrompt()
    while True:
        queue.Examine()
        userInput = state.prompt()
        ok, action, args = inputparser.parse(userInput)
        if ok:
            action(state, *args)
            io.output("")
            state.Examine()
        else:
            errMsg = action
            io.output(errMsg)
            io.output("")
