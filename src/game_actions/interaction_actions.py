"""
interaction_actions.py

Object interaction action functions.
Handles eating, phone calls, watching TV, and other object interactions.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .action_decorators import attempt, thingify

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from ..core.game_objects import Object
    from ..core.items import Food

# Type alias for game state
GameStateType = 'GameState'


def call_phone(state: 'GameState') -> None:
    """Make a phone call using the main room phone."""
    phone = state.apartment.main.phone
    if state.hero.GetRoom() != phone.GetRoom():
        state.hero.io.output("I need to get close to the phone first.")
        return
    attempt(lambda: phone.Interact(state.hero), "I can't call.", state.hero)


def rolodex(state: 'GameState') -> None:
    """Display the phone numbers available to call."""
    phone = state.apartment.main.phone
    if state.hero.GetRoom() != phone.GetRoom():
        state.hero.io.output("I need to get close to the phone first.")
        return
    attempt(lambda: phone.Rolodex(state.hero), "No numbers.", state.hero)


def eat_thing(state: 'GameState', food_name: str) -> None:
    """Eat food from the fridge to restore feel."""
    # Import here to avoid circular imports
    from ..core.items import Food
    
    fridge = state.apartment.main.fridge
    if state.hero.GetRoom() != fridge.GetRoom():
        state.hero.io.output("Step a little closer to the fridge.")
        return

    if fridge.isClosed():
        state.hero.io.output("Right, I have to open the fridge first.")
        return

    food = state.apartment.main.fridge.GetFirstItemByName(food_name)
    if isinstance(food, Food):
        attempt(lambda: food.Eat(state.hero), "Error!", state.hero)
    else:
        state.hero.io.output("I don't see that food in there.")


@thingify
def watch_tv(state: 'GameState', tv: 'Object') -> None:
    """Watch the TV to see the news."""
    if tv.name != 'tv':
        state.hero.io.output("I don't know how to watch that!  Not for very long, at least.")
    else:
        attempt(lambda: tv.Examine(state.hero), "Yeah, I don't know.", state.hero)


def mail_check(state: 'GameState') -> None:
    """Mail a check to get money tomorrow."""
    check = state.hero.GetFirstItemByName("check")
    if check:
        tomorrow = state.watch.curr_time + timedelta(days=1)

        def mail(_curr_time: datetime, _event_time: datetime) -> None:
            state.hero.io.output("new bank deposit!")
            state.hero.curr_balance += 100
        if state.event_queue is not None:
            state.event_queue.AddEvent(mail, tomorrow)
        state.hero.Destroy([check])
        state.hero.io.output("Check is out.  Big money tomorrow!")
    else:
        state.hero.io.output("You're not holding a check.  How's the cabinet looking?")


def take_ice_bath(state: 'GameState') -> None:
    """Take an ice bath in the bathroom to boost feel using ice cubes."""
    # Check if hero is in bathroom
    if state.hero.GetRoom() != state.apartment.bathroom:
        state.hero.io.output("I need to be in the bathroom to take an ice bath.")
        return
    
    # Check if hero has ice cubes
    ice_cubes = state.hero.GetFirstItemByName("ice-cubes")
    if not ice_cubes:
        state.hero.io.output("I need ice cubes to take an ice bath.")
        return
    
    # Consume the ice cubes
    state.hero.Destroy([ice_cubes])
    
    # Boost feel by 40
    state.hero.feel += 40
    
    # Advance time by 1 hour
    state.watch.curr_time += timedelta(hours=1)
    
    # Output success message
    state.hero.io.output("You fill the tub with cold water and add the ice cubes.")
    state.hero.io.output("The shock of the cold water makes you incredibly alert!")
    state.hero.io.output("Time passes as you endure the ice bath...")
    state.hero.io.output(f"You feel much more alert. (Feel: {state.hero.feel})")