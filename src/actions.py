# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from typing import Callable, Any
from .gamestate import Container, Object, Openable, Closet

# Type alias for game state
GameStateType = Any  # Forward reference to avoid circular imports


def prompt(s: str) -> str:
    return input(s)


def emit(s: str) -> None:
    print(s)
    print()


def attempt(thunk: Callable[[], None], error_msg: str) -> None:
    try:
        thunk()
    except AttributeError as e:
        print(error_msg, e)


def thingify(func: Callable[[GameStateType, Any], None]) -> Callable[[GameStateType, str], None]:
    def inner(state: GameStateType, arg: str) -> None:
        room_object = state.hero.GetRoom().GetFirstItemByName(arg)
        if room_object:
            func(state, room_object)
        else:
            print("I don't see that in the room.")

    return inner


def DebugItems(state: GameStateType) -> None:
    # Give me a few things to play with

    hammer = Object("hammer", state.apartment.main)
    nails = Object("box-of-nails", state.apartment.main)
    plywood = Object("plywood-sheet", state.apartment.main)

    state.hero.Pickup(hammer)
    state.hero.Pickup(nails)
    state.hero.Pickup(plywood)


def CallPhone(state: GameStateType) -> None:
    state.apartment.main.phone.Interact(state.hero)


def Rolodex(state: GameStateType) -> None:
    phone = state.apartment.main.phone
    phone.Rolodex(state.hero)


def LookAtWatch(state: GameStateType) -> None:
    watch = state.hero.GetFirstItemByName("watch")
    if watch:
        watch.Interact(state.hero)
    else:
        print("Not carrying a watch!")
        print()


def Ponder(state: GameStateType) -> None:
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            num_hours = int(length)
            if num_hours > 1000:  # TODO: make this shorter.
                emit("\nThat's too long to sit and do nothing.")
                continue
            else:
                break
        else:
            emit("\nWhat? Give me a number.")

    state.watch.currTime += timedelta(hours=num_hours)
    state.hero.feel -= 10 * num_hours


def CheckBalance(state: GameStateType) -> None:
    emit(f"Current Balance: ${state.hero.currBalance}")


def CheckFeel(state: GameStateType) -> None:
    feel = state.hero.feel
    if feel >= 40:
        emit("Feeling good")
    elif feel >= 20:
        emit("Feeling okay")
    else:
        emit("I'm about to hit the sheets!")


def MailCheck(state: GameStateType) -> None:
    check = state.hero.GetFirstItemByName("check")
    if check:
        tomorrow = state.watch.currTime + timedelta(days=1)

        def mail(a: Any, b: Any) -> None:
            print("new bank deposit!")
            state.hero.currBalance += 100
        state.eventQueue.AddEvent(mail, tomorrow)
        state.hero.Destroy([check])
        print("Check is out.  Big money tomorrow!")
    else:
        print("You're not holding a check.  How's the cabinet looking?")


def InspectRoom(state: GameStateType) -> None:
    room = state.hero.GetRoom()
    print()
    print("You look around the room.  You see:")
    print()

    if not room.contents:
        print("Nothing!")

    for item in room.contents:
        print(item)
    print()


def EatThing(state: GameStateType, food_name: str) -> None:
    fridge = state.apartment.main.fridge
    if state.hero.GetRoom() != fridge.GetRoom():
        print("Step a little closer to the fridge.")
        return

    if fridge.isClosed():
        print("Right, I have to open the fridge first.")
        return

    food = state.apartment.main.fridge.GetFirstItemByName(food_name)
    if food:
        attempt(lambda: food.Eat(state.hero), "Error!")
    else:
        print("I don't see that food in there.")


@thingify
def ExamineThing(state: GameStateType, room_object: Any) -> None:
    attempt(lambda: room_object.Examine(state.hero),
            "I don't know how to examine that.")


@thingify
def WatchTv(state: GameStateType, tv: Any) -> None:
    if tv.name != 'tv':
        print("I don't know how to watch that!  Not for very long, at least.")
    else:
        attempt(lambda: tv.Examine(state.hero), "Yeah, I don't know.")


@thingify
def OpenThing(state: GameStateType, room_object: Any) -> None:
    attempt(lambda: room_object.Open(state.hero), "I can't open that.")


@thingify
def CloseThing(state: GameStateType, room_object: Any) -> None:
    attempt(lambda: room_object.Close(state.hero), "I can't close that.")


def GetObject(state: GameStateType, obj: str, room_object: Any) -> None:
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


def Inventory(state: GameStateType) -> None:
    objs = state.hero.contents
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print("\nYou are carrying the following:")

    for obj in objs:
        print("    ", obj)

    print()


def EnterRoom(state: GameStateType, room_name: str) -> None:
    to_room = state.apartment.GetFirstItemByName(room_name)
    if to_room:
        from_room = state.hero.GetRoom()
        if to_room == from_room:
            print("Already there.")
        else:
            attempt(lambda: to_room.Enter(
                from_room, state.hero), "I can't enter.")
    else:
        print("I haven't built that wing yet.")


def NailSelfIn(state: GameStateType) -> None:
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
