"""
inventory_actions.py

Inventory management action functions.
Handles pickup, examine, inventory display, and container operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .action_decorators import attempt, thingify

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from ..core.game_objects import Object, Container, Openable

# Type alias for game state  
GameStateType = 'GameState'


@thingify
def examine_thing(state: 'GameState', room_object: 'Object') -> None:
    """Examine an object in the current room."""
    attempt(lambda: room_object.Examine(state.hero), "I can't examine that.", state.hero)


@thingify
def open_thing(state: 'GameState', room_object: 'Object') -> None:
    """Open a container in the current room."""
    attempt(lambda: room_object.Open(state.hero), "I can't open that.", state.hero)


@thingify
def close_thing(state: 'GameState', room_object: 'Object') -> None:
    """Close a container in the current room."""
    attempt(lambda: room_object.Close(state.hero), "I can't close that.", state.hero)


def get_object(state: 'GameState', obj: str, room_object: str) -> None:
    """Get an object from a container in the current room."""
    # Import here to avoid circular imports
    from ..core.game_objects import Container, Openable
    
    room_obj = state.hero.GetRoom().GetFirstItemByName(room_object)
    if room_obj:
        if isinstance(room_obj, Openable):
            openable = room_obj
            if openable.state == Openable.State.OPEN:
                thing = openable.GetFirstItemByName(obj)
                if thing:
                    state.hero.Pickup(thing)
                else:
                    state.hero.io.output(f"I don't see that in the {openable.name}.")
            else:
                state.hero.io.output("Try opening it first.")
        elif isinstance(room_obj, Container):
            container = room_obj
            thing = container.GetFirstItemByName(obj)
            if thing:
                state.hero.Pickup(thing)
            else:
                state.hero.io.output(f"I don't see that on the {container.name}.")
        else:
            state.hero.io.output("How could I do that?")
    else:
        state.hero.io.output("I don't see that in the room.")

    state.hero.io.output("")


def inventory(state: 'GameState') -> None:
    """Display the hero's current inventory."""
    objs = state.hero.contents
    if not objs:
        state.hero.io.output("\nYou have no objects in your inventory")
        state.hero.io.output("")
        return

    state.hero.io.output("\nYou are carrying the following:")

    for obj in objs:
        state.hero.io.output(f"     {obj}")

    state.hero.io.output("")