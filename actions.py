# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from gamestate import GameState, Container, Object, Openable

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

def attempt(thunk, errorMsg):
    try:
        thunk()
    except AttributeError:
        print errorMsg

def thingify(func):
    def inner(state, arg):
        roomObject = state.hero.GetRoom().GetFirstItemByName(arg)
        if roomObject:
            func(state, roomObject)
        else:
            print "I don't see that in the room."

    return inner

def DebugItems(state):
    # Give me a few things to play with

    hammer  = Object("hammer", state.apartment.main)
    nails   = Object("box-of-nails", state.apartment.main)
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
        print "Not carrying a watch!"
        print

def Ponder(state):
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            numHours = int(length)
            if numHours > 1000: # TODO: make this shorter.
                emit("\nThat's too long to sit and do nothing.")
                continue
            else:
                break
        else:
            emit("\nWhat? Give me a number.")

    state.watch.currTime += timedelta(hours=numHours)
    state.hero.feel -= 10 * numHours

def CheckBalance(state):
    emit("Current Balance: ${0}".format(state.hero.currBalance))

def CheckFeel(state):
    feel = state.hero.feel
    if feel >= 40:
        emit("Feeling good")
    elif feel >= 20:
        emit("Feeling okay")
    else:
        emit("I'm about to hit the sheets!")

@thingify
def ExamineThing(state, roomObject):
    attempt(lambda: roomObject.Examine(state.hero), "I don't know how to examine that.")

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
                    print "I don't see that in the {}.".format(openable.name)
            else:
                print "Try opening it first."
        elif isinstance(roomObject, Container):
            container = roomObject
            thing = container.GetFirstItemByName(obj)
            if thing:
                state.hero.Pickup(thing)
            else:
                print "I don't see that on the {}.".format(container.name)
        else:
            print "How could I do that?"
    else:
        print "I don't see that in the room."

    print

def Inventory(state):
    objs = state.hero.contents
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print "\nYou are carrying the following:"

    for obj in objs:
        print "    ", obj

    print

def EnterCloset(state):
    if state.currFSMState == GameState.CLOSET_READY:
        emit("\nYou are in a very nice closet already")
        return
    if state.currFSMState != GameState.APARTMENT_READY:
        emit("\nThat would be very difficult from your current location")
        return

    state.currFSMState = GameState.CLOSET_READY

    emit("\nYou are now in the closet")

def LeaveCloset(state):
    if state.currFSMState == GameState.CLOSET_NAILED:
        emit("\nPerhaps you should ponder exactly how you'll do that?")
        return

    if state.currFSMState != GameState.CLOSET_READY:
        emit("\nThat would be very difficult from your current location")
        return

    if state.currFSMState == GameState.CLOSET_READY:
        emit("\nYou have left the closet and are now back in your apartment's main room");
        state.currFSMState = GameState.APARTMENT_READY
        return

def NailSelfIn(state):
    if state.currFSMState == GameState.CLOSET_NAILED:
        emit("\nWasn't once enough?")
        return

    if state.currFSMState != GameState.CLOSET_READY:
        emit("\nThat would be very difficult from your current location")
        return

    hero = state.hero

    if not hero.contents:
        emit("\nYou have no objects with which to do that")
        return

    hammer  = hero.GetFirstItemByName('hammer')
    nails   = hero.GetFirstItemByName('box-of-nails')
    plywood = hero.GetFirstItemByName('plywood-sheet')

    if not hammer or not nails or not plywood:
        if not plywood:
            s = 'Perhaps some wood?'
        if not hammer:
            s = 'Perhaps a hammer?'
        if not nails:
            s = 'Perhaps some nails?'

        emit("\nYou are missing something.  %s" % s)
        return

    hero.Destroy([plywood])

    emit("\nYou have successfully nailed yourself into a rather small closet.")

    state.currFSMState = GameState.CLOSET_NAILED

    numHours = 2
    state.watch.currTime += timedelta(hours=numHours)
    hero.feel -= 10 * numHours
