from __future__ import annotations

from datetime import datetime, timedelta

from . import inputparser
from . import delivery
from .gamestate import GameState, Object
from .io_interface import IOInterface, ConsoleIO
from .endings import GameEndings
from .commands.game_commands import LetGoCommand, HoldOnCommand

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
    while not state.game_over:
        queue.Examine()

        # Day 7+ ending check (before prompt, not during dream)
        if not state.in_dream_confrontation:
            ending = GameEndings.check_ending(state)
            if ending and not state.game_over:
                if ending == "victory":
                    GameEndings.display_victory(io)
                elif ending == "partial_victory":
                    GameEndings.display_partial_victory(io)
                elif ending == "defeat":
                    GameEndings.display_defeat(io)
                state.game_over = True
                state.ending_type = ending
                break

        # Dream confrontation: restrict input to let go / hold on
        if state.in_dream_confrontation:
            userInput = state.io.get_input("What do you do?: ")
            ok, command_or_error = inputparser.parse(userInput, io)
            if ok and isinstance(command_or_error, (LetGoCommand, HoldOnCommand)):
                result = state.command_invoker.execute_command(
                    command_or_error, state
                )
                if result.message:
                    io.output(result.message)
                io.output("")
            else:
                io.output("The voice echoes in the darkness. What do you do?")
                io.output("")
            continue

        # Normal game loop
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
