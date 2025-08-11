"""
utility_actions.py

Utility and debug action functions.
Handles debug commands, status checks, time functions, and administrative actions.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from ..core.items import Watch

# Type alias for game state
GameStateType = 'GameState'


def debug_items(state: 'GameState') -> None:
    """Give the player some debug items to play with."""
    # Import here to avoid circular imports
    from ..core.game_objects import Object
    from ..core.items import Food
    
    # Give me a few things to play with
    hammer = Object("hammer", state.apartment.main)
    nails = Object("box-of-nails", state.apartment.main)
    plywood = Object("plywood-sheet", state.apartment.main)
    ice_cubes = Food("ice-cubes", state.apartment.main, 2)  # 2 feel boost like normal ice cubes

    state.hero.Pickup(hammer)
    state.hero.Pickup(nails)
    state.hero.Pickup(plywood)
    state.hero.Pickup(ice_cubes)


def look_at_watch(state: 'GameState') -> None:
    """Check the current time on the hero's watch."""
    # Import here to avoid circular imports
    from ..core.items import Watch
    
    watch = state.hero.GetFirstItemByName("watch")
    if watch and isinstance(watch, Watch):
        watch.Interact(state.hero)
    else:
        state.hero.io.output("Not carrying a watch!")
        state.hero.io.output("")


def ponder(state: 'GameState') -> None:
    """Spend time pondering, advancing the clock and reducing feel."""
    while True:
        length = state.hero.io.get_input("How many hours?: ")
        if length.isdigit():
            num_hours = int(length)
            if num_hours > 1000:
                state.hero.io.output("\nThat's too long to sit and do nothing.")
                state.hero.io.output("")
                continue
            break
        else:
            state.hero.io.output("\nWhat? Give me a number.")
            state.hero.io.output("")

    state.watch.curr_time += timedelta(hours=num_hours)
    state.hero.feel -= 10 * num_hours


def check_balance(state: 'GameState') -> None:
    """Display the hero's current money balance."""
    state.hero.io.output(f"Current Balance: ${state.hero.curr_balance}")
    state.hero.io.output("")


def check_feel(state: 'GameState') -> None:
    """Display the hero's current feel/energy level."""
    feel = state.hero.feel
    if feel >= 40:
        state.hero.io.output("Feeling good")
    elif feel >= 20:
        state.hero.io.output("Feeling okay")
    else:
        state.hero.io.output("I'm about to hit the sheets!")
    state.hero.io.output("")