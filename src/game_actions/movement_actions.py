"""
movement_actions.py

Movement and room navigation action functions.
Handles room transitions, entering/leaving rooms, and special room actions.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from .action_decorators import attempt

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from ..core.rooms import Room, Closet

# Type alias for game state
GameStateType = 'GameState'


def enter_room(state: 'GameState', room_name: str) -> None:
    """Move the hero to a different room."""
    # Import here to avoid circular imports
    from ..core.rooms import Room
    
    to_room = state.apartment.GetFirstItemByName(room_name)
    if to_room and isinstance(to_room, Room):
        from_room = state.hero.GetRoom()
        if to_room == from_room:
            state.hero.io.output("Already there.")
        else:
            attempt(lambda: to_room.Enter(
                from_room, state.hero), "I can't enter.", state.hero)
    else:
        state.hero.io.output("I haven't built that wing yet.")


def nail_self_in(state: 'GameState') -> None:
    """Nail yourself into the closet using hammer, nails, and plywood."""
    # Import here to avoid circular imports
    from ..core.rooms import Closet
    
    closet = state.apartment.closet

    if state.hero.GetRoom() != closet:
        state.hero.io.output("Gotta be in the closet to start nailing!")
        return

    if closet.state == Closet.State.NAILED:
        state.hero.io.output("\nWasn't once enough?")
        return

    hero = state.hero

    if not hero.contents:
        state.hero.io.output("\nYou have no objects with which to do that")
        return

    hammer = hero.GetFirstItemByName('hammer')
    nails = hero.GetFirstItemByName('box-of-nails')
    plywood = hero.GetFirstItemByName('plywood-sheet')

    if not hammer or not nails or not plywood:
        s = ''
        if not plywood:
            s = 'Perhaps some wood?'
        elif not hammer:
            s = 'Perhaps a hammer?'
        elif not nails:
            s = 'Perhaps some nails?'

        state.hero.io.output(f"\nYou are missing something.  {s}")
        return

    hero.Destroy([plywood, nails])

    state.hero.io.output("\nYou have successfully nailed yourself into a rather small closet.")

    closet.state = Closet.State.NAILED

    num_hours = 2
    state.watch.curr_time += timedelta(hours=num_hours)
    hero.feel -= 10 * num_hours


def inspect_room(state: 'GameState') -> None:
    """Look around the current room and list all objects."""
    room = state.hero.GetRoom()
    state.hero.io.output("")
    state.hero.io.output("You look around the room.  You see:")
    state.hero.io.output("")

    if not room.contents:
        state.hero.io.output("Nothing!")

    for item in room.contents:
        state.hero.io.output(str(item))
    state.hero.io.output("")