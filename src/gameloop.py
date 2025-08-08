from __future__ import annotations

from datetime import datetime, timedelta

from . import inputparser
from . import delivery
from .gamestate import GameState, Object
from .io_interface import IOInterface, ConsoleIO

from .delivery import EventQueue


def run(io: IOInterface | None = None) -> None:
    if io is None:
        io = ConsoleIO()
    
    state = GameState(io)
    queue = EventQueue(state)
    state.SetEventQueue(queue)

    def DeliverCheck(currTime: datetime, eventTime: datetime) -> None:
        io.output("Government check in the mail!")
        Object("check", state.apartment.main.cabinet)
        queue.AddEvent(DeliverCheck, eventTime + timedelta(weeks=2))

    queue.AddEvent(DeliverCheck, state.watch.curr_time + timedelta(weeks=2))
    state.IntroPrompt()
    while True:
        queue.Examine()
        userInput = state.prompt()
        ok, command_or_error = inputparser.parse(userInput, io)
        if ok:
            command = command_or_error
            # Execute command through the command invoker and add to history
            result = state.command_invoker.execute_command(command, state)
            
            # Add successful commands to history for undo/redo
            if result.success:
                state.command_history.add_command(command)
            
            # Display command result message if provided
            if result.message:
                io.output(result.message)
                
            io.output("")
            state.Examine()
        else:
            errMsg = command_or_error
            io.output(errMsg)
            io.output("")
