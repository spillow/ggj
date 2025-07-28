# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from .gamestate import GameState, Container, Object, Openable, Closet


def prompt(s):
    return input(s)


def emit(s):
    print(s)
    print()


def attempt(thunk, errorMsg):
    try:
        thunk()
    except AttributeError as e:
        print(errorMsg, e)


def thingify(func):
    def inner(state, arg):
        roomObject = state.hero.GetRoom().GetFirstItemByName(arg)
        if roomObject:
            func(state, roomObject)
        else:
            print("I don't see that in the room.")

    return inner


def DebugItems(state):
    # Give me a few things to play with

    hammer = Object("hammer", state.apartment.main)
    nails = Object("box-of-nails", state.apartment.main)
    plywood = Object("plywood-sheet", state.apartment.main)

    state.hero.Pickup(hammer)
    state.hero.Pickup(nails)
    state.hero.Pickup(plywood)


def CallPhone(state):
    state.apartment.main.phone.Interact(state.hero)


def Rolodex(state):
    phone = state.apartment.main.phone
    phone.Rolodex(state.hero)


def LookAtWatch(state):
    watch = state.hero.GetFirstItemByName("watch")
    if watch:
        watch.Interact(state.hero)
    else:
        print("Not carrying a watch!")
        print()


def Ponder(state):
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            numHours = int(length)
            if numHours > 1000:  # TODO: make this shorter.
                emit("\nThat's too long to sit and do nothing.")
                continue
            else:
                break
        else:
            emit("\nWhat? Give me a number.")

    state.watch.currTime += timedelta(hours=numHours)
    state.hero.feel -= 10 * numHours


def CheckBalance(state):
    emit(f"Current Balance: ${state.hero.currBalance}")


def CheckFeel(state):
    feel = state.hero.feel
    if feel >= 40:
        emit("Feeling good")
    elif feel >= 20:
        emit("Feeling okay")
    else:
        emit("I'm about to hit the sheets!")


def MailCheck(state):
    check = state.hero.GetFirstItemByName("check")
    if check:
        tomorrow = state.watch.currTime + timedelta(days=1)

        def mail(a, b):
            print("new bank deposit!")
            state.hero.currBalance += 100
        state.eventQueue.AddEvent(mail, tomorrow)
        state.hero.Destroy([check])
        print("Check is out.  Big money tomorrow!")
    else:
        print("You're not holding a check.  How's the cabinet looking?")


def InspectRoom(state):
    room = state.hero.GetRoom()
    print()
    print("You look around the room.  You see:")
    print()

    if not room.contents:
        print("Nothing!")

    for item in room.contents:
        print(item)
    print()


def EatThing(state, foodName):
    fridge = state.apartment.main.fridge
    if state.hero.GetRoom() != fridge.GetRoom():
        print("Step a little closer to the fridge.")
        return

    if fridge.isClosed():
        print("Right, I have to open the fridge first.")
        return

    food = state.apartment.main.fridge.GetFirstItemByName(foodName)
    if food:
        attempt(lambda: food.Eat(state.hero), "Error!")
    else:
        print("I don't see that food in there.")


@thingify
def ExamineThing(state, roomObject):
    attempt(lambda: roomObject.Examine(state.hero),
            "I don't know how to examine that.")


@thingify
def WatchTv(state, tv):
    if tv.name != 'tv':
        print("I don't know how to watch that!  Not for very long, at least.")
    else:
        attempt(lambda: tv.Examine(state.hero), "Yeah, I don't know.")


@thingify
def OpenThing(state, roomObject):
    attempt(lambda: roomObject.Open(state.hero), "I can't open that.")


@thingify
def CloseThing(state, roomObject):
    attempt(lambda: roomObject.Close(state.hero), "I can't close that.")


def GetObject(state, obj, roomObject):
    roomObject = state.hero.GetRoom().GetFirstItemByName(roomObject)
    if roomObject:
        if isinstance(roomObject, Openable):
            openable = roomObject
            if openable.state == Openable.State.OPEN:
                thing = openable.GetFirstItemByName(obj)
                if thing:
                    state.hero.Pickup(thing)
                else:
                    print(f"I don't see that in the {openable.name}.")
            else:
                print("Try opening it first.")
        elif isinstance(roomObject, Container):
            container = roomObject
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


def Inventory(state):
    objs = state.hero.contents
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print("\nYou are carrying the following:")

    for obj in objs:
        print("    ", obj)

    print()


def EnterRoom(state, roomName):
    toRoom = state.apartment.GetFirstItemByName(roomName)
    if toRoom:
        fromRoom = state.hero.GetRoom()
        if toRoom == fromRoom:
            print("Already there.")
        else:
            attempt(lambda: toRoom.Enter(
                fromRoom, state.hero), "I can't enter.")
    else:
        print("I haven't built that wing yet.")


def NailSelfIn(state):
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
        if not plywood:
            s = 'Perhaps some wood?'
        if not hammer:
            s = 'Perhaps a hammer?'
        if not nails:
            s = 'Perhaps some nails?'

        print("\nYou are missing something.  %s" % s)
        return

    hero.Destroy([plywood])

    print("\nYou have successfully nailed yourself into a rather small closet.")

    closet.state = Closet.CLOSET_NAILED

    numHours = 2
    state.watch.currTime += timedelta(hours=numHours)
    hero.feel -= 10 * numHours
