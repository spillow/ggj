"""Actions module for the text-based adventure game.

Action functions that a user could possibly execute.
Actions are responsible for updating the given gamestate
and supplying any kind of feedback with regards to not
being able perform an action.

Actions do take time so each should implement how they move
the clock forward.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from .gamestate import Container, Object, Openable, Closet, GameState, Food, Room, Phone, Watch, Hero

# Type alias for game state
GameStateType = GameState


def attempt(thunk: Callable[[], None], error_msg: str, hero: Hero) -> None:
    """Attempt to execute a function, catching AttributeError."""
    try:
        thunk()
    except AttributeError as e:
        hero.io.output(f"{error_msg} {e}")


def thingify(func: Callable[[GameStateType, Object], None]) -> Callable[[GameStateType, str], None]:
    """Decorator to convert a function that takes an object to one that takes a string name."""
    def inner(state: GameStateType, arg: str) -> None:
        room_object = state.hero.GetRoom().GetFirstItemByName(arg)
        if room_object:
            func(state, room_object)
        else:
            state.hero.io.output("I don't see that in the room.")

    return inner


def debug_items(state: GameStateType) -> None:
    """Give the player some debug items to play with."""
    # Give me a few things to play with

    hammer = Object("hammer", state.apartment.main)
    nails = Object("box-of-nails", state.apartment.main)
    plywood = Object("plywood-sheet", state.apartment.main)

    state.hero.Pickup(hammer)
    state.hero.Pickup(nails)
    state.hero.Pickup(plywood)


def call_phone(state: GameStateType) -> None:
    """Make a phone call using the main room phone."""
    phone: Phone = state.apartment.main.phone
    phone.Interact(state.hero)


def rolodex(state: GameStateType) -> None:
    """Show the phone's rolodex of available numbers."""
    phone: Phone = state.apartment.main.phone
    phone.Rolodex(state.hero)


def look_at_watch(state: GameStateType) -> None:
    """Check the current time on the hero's watch."""
    watch = state.hero.GetFirstItemByName("watch")
    if watch and isinstance(watch, Watch):
        watch.Interact(state.hero)
    else:
        state.hero.io.output("Not carrying a watch!")
        state.hero.io.output("")


def ponder(state: GameStateType) -> None:
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


def check_balance(state: GameStateType) -> None:
    """Display the hero's current money balance."""
    state.hero.io.output(f"Current Balance: ${state.hero.curr_balance}")
    state.hero.io.output("")


def check_feel(state: GameStateType) -> None:
    """Display the hero's current feel/energy level."""
    feel = state.hero.feel
    if feel >= 40:
        state.hero.io.output("Feeling good")
    elif feel >= 20:
        state.hero.io.output("Feeling okay")
    else:
        state.hero.io.output("I'm about to hit the sheets!")
    state.hero.io.output("")


def mail_check(state: GameStateType) -> None:
    """Mail a check, scheduling money to arrive tomorrow."""
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


def inspect_room(state: GameStateType) -> None:
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


def eat_thing(state: GameStateType, food_name: str) -> None:
    """Eat food from the fridge to restore feel."""
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
def examine_thing(state: GameStateType, room_object: Object) -> None:
    """Examine an object in the current room."""
    attempt(lambda: room_object.Examine(state.hero),
            "I don't know how to examine that.", state.hero)


@thingify
def watch_tv(state: GameStateType, tv: Object) -> None:
    """Watch the TV to see the news."""
    if tv.name != 'tv':
        state.hero.io.output("I don't know how to watch that!  Not for very long, at least.")
    else:
        attempt(lambda: tv.Examine(state.hero), "Yeah, I don't know.", state.hero)


@thingify
def open_thing(state: GameStateType, room_object: Object) -> None:
    """Open a container in the current room."""
    attempt(lambda: room_object.Open(state.hero), "I can't open that.", state.hero)


@thingify
def close_thing(state: GameStateType, room_object: Object) -> None:
    """Close a container in the current room."""
    attempt(lambda: room_object.Close(state.hero), "I can't close that.", state.hero)


def get_object(state: GameStateType, obj: str, room_object: str) -> None:
    """Get an object from a container in the current room."""
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


def inventory(state: GameStateType) -> None:
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


def enter_room(state: GameStateType, room_name: str) -> None:
    """Move the hero to a different room."""
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


def nail_self_in(state: GameStateType) -> None:
    """Nail yourself into the closet using hammer, nails, and plywood."""
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
