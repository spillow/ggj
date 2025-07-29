"""Actions module for the text-based adventure game.

Action functions that a user could possibly execute.
Actions are responsible for updating the given gamestate
and supplying any kind of feedback with regards to not
being able perform an action.

Actions do take time so each should implement how they move
the clock forward.
"""

from datetime import timedelta
from typing import Callable, Any
from .gamestate import Container, Object, Openable, Closet, GameState, Food, Room, Phone, Watch

# Type alias for game state
GameStateType = GameState


def prompt(s: str) -> str:
    """Prompt the user for input."""
    return input(s)


def emit(s: str) -> None:
    """Print a message with a blank line after."""
    print(s)
    print()


def attempt(thunk: Callable[[], None], error_msg: str) -> None:
    """Attempt to execute a function, catching AttributeError."""
    try:
        thunk()
    except AttributeError as e:
        print(error_msg, e)


def thingify(func: Callable[[GameStateType, Any], None]) -> Callable[[GameStateType, str], None]:
    """Decorator to convert a function that takes an object to one that takes a string name."""
    def inner(state: GameStateType, arg: str) -> None:
        room_object = state.hero.GetRoom().GetFirstItemByName(arg)
        if room_object:
            func(state, room_object)
        else:
            print("I don't see that in the room.")

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
        print("Not carrying a watch!")
        print()


def ponder(state: GameStateType) -> None:
    """Spend time pondering, advancing the clock and reducing feel."""
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            num_hours = int(length)
            if num_hours > 1000:
                emit("\nThat's too long to sit and do nothing.")
                continue
            break
        else:
            emit("\nWhat? Give me a number.")

    state.watch.currTime += timedelta(hours=num_hours)
    state.hero.feel -= 10 * num_hours


def check_balance(state: GameStateType) -> None:
    """Display the hero's current money balance."""
    emit(f"Current Balance: ${state.hero.currBalance}")


def check_feel(state: GameStateType) -> None:
    """Display the hero's current feel/energy level."""
    feel = state.hero.feel
    if feel >= 40:
        emit("Feeling good")
    elif feel >= 20:
        emit("Feeling okay")
    else:
        emit("I'm about to hit the sheets!")


def mail_check(state: GameStateType) -> None:
    """Mail a check, scheduling money to arrive tomorrow."""
    check = state.hero.GetFirstItemByName("check")
    if check:
        tomorrow = state.watch.currTime + timedelta(days=1)

        def mail(_a: Any, _b: Any) -> None:
            print("new bank deposit!")
            state.hero.currBalance += 100
        state.eventQueue.AddEvent(mail, tomorrow)
        state.hero.Destroy([check])
        print("Check is out.  Big money tomorrow!")
    else:
        print("You're not holding a check.  How's the cabinet looking?")


def inspect_room(state: GameStateType) -> None:
    """Look around the current room and list all objects."""
    room = state.hero.GetRoom()
    print()
    print("You look around the room.  You see:")
    print()

    if not room.contents:
        print("Nothing!")

    for item in room.contents:
        print(item)
    print()


def eat_thing(state: GameStateType, food_name: str) -> None:
    """Eat food from the fridge to restore feel."""
    fridge = state.apartment.main.fridge
    if state.hero.GetRoom() != fridge.GetRoom():
        print("Step a little closer to the fridge.")
        return

    if fridge.isClosed():
        print("Right, I have to open the fridge first.")
        return

    food = state.apartment.main.fridge.GetFirstItemByName(food_name)
    if isinstance(food, Food):
        attempt(lambda: food.Eat(state.hero), "Error!")
    else:
        print("I don't see that food in there.")


@thingify
def examine_thing(state: GameStateType, room_object: Any) -> None:
    """Examine an object in the current room."""
    attempt(lambda: room_object.Examine(state.hero),
            "I don't know how to examine that.")


@thingify
def watch_tv(state: GameStateType, tv: Any) -> None:
    """Watch the TV to see the news."""
    if tv.name != 'tv':
        print("I don't know how to watch that!  Not for very long, at least.")
    else:
        attempt(lambda: tv.Examine(state.hero), "Yeah, I don't know.")


@thingify
def open_thing(state: GameStateType, room_object: Any) -> None:
    """Open a container in the current room."""
    attempt(lambda: room_object.Open(state.hero), "I can't open that.")


@thingify
def close_thing(state: GameStateType, room_object: Any) -> None:
    """Close a container in the current room."""
    attempt(lambda: room_object.Close(state.hero), "I can't close that.")


def get_object(state: GameStateType, obj: str, room_object: Any) -> None:
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
                    print(f"I don't see that in the {openable.name}.")
            else:
                print("Try opening it first.")
        elif isinstance(room_obj, Container):
            container = room_obj
            thing = container.GetFirstItemByName(obj)
            if thing:
                state.hero.Pickup(thing)
            else:
                print(f"I don't see that on the {container.name}.")
        else:
            print("How could I do that?")
    else:
        print("I don't see that in the room.")

    print()


def inventory(state: GameStateType) -> None:
    """Display the hero's current inventory."""
    objs = state.hero.contents
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print("\nYou are carrying the following:")

    for obj in objs:
        print("    ", obj)

    print()


def enter_room(state: GameStateType, room_name: str) -> None:
    """Move the hero to a different room."""
    to_room = state.apartment.GetFirstItemByName(room_name)
    if to_room and isinstance(to_room, Room):
        from_room = state.hero.GetRoom()
        if to_room == from_room:
            print("Already there.")
        else:
            attempt(lambda: to_room.Enter(
                from_room, state.hero), "I can't enter.")
    else:
        print("I haven't built that wing yet.")


def nail_self_in(state: GameStateType) -> None:
    """Nail yourself into the closet using hammer, nails, and plywood."""
    closet = state.apartment.closet

    if state.hero.GetRoom() != closet:
        print("Gotta be in the closet to start nailing!")
        return

    if closet.state == Closet.CLOSET_NAILED:
        print("\nWasn't once enough?")
        return

    hero = state.hero

    if not hero.contents:
        print("\nYou have no objects with which to do that")
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

        print(f"\nYou are missing something.  {s}")
        return

    hero.Destroy([plywood])

    print("\nYou have successfully nailed yourself into a rather small closet.")

    closet.state = Closet.CLOSET_NAILED

    num_hours = 2
    state.watch.currTime += timedelta(hours=num_hours)
    hero.feel -= 10 * num_hours
