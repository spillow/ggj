"""
action_decorators.py

Decorators for action functions including @thingify and utility decorators.
Provides common functionality for action validation and error handling.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game_objects import Object
    from ..core.characters import Hero
    from ..core.game_world import GameState

# Type alias for game state
GameStateType = 'GameState'


def attempt(thunk: Callable[[], None], error_msg: str, hero: 'Hero') -> None:
    """Attempt to execute a function, catching AttributeError."""
    try:
        thunk()
    except AttributeError as e:
        hero.io.output(f"{error_msg} {e}")


def thingify(func: Callable[['GameState', 'Object'], None]) -> Callable[['GameState', str], None]:
    """Decorator to convert a function that takes an object to one that takes a string name."""
    def inner(state: 'GameState', arg: str) -> None:
        room_object = state.hero.GetRoom().GetFirstItemByName(arg)
        if room_object:
            func(state, room_object)
        else:
            state.hero.io.output("I don't see that in the room.")

    return inner


def sameroom(func: Callable[..., None]) -> Callable[..., None]:
    """
    Decorator to ensure that the hero and the object are in the same room before
    allowing interaction.
    """
    def check(self: 'Object', hero: 'Hero') -> None:
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            hero.io.output(f"Must be in the same room as the {self.name}")

    return check