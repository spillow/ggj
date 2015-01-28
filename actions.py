# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from gamestate import GameState, Container, Object, Surface

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

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

def ExamineToolbox(state):
    toolbox = state.apartment.main.toolbox
    if toolbox.state != Container.State.OPEN:
        print "The toolbox must be opened first."
        return

    if not toolbox.contents:
        print "nothing in the toolbox."
        print
    else:
        print "toolbox contains:"
        for item in toolbox.contents:
            print "    {0}".format(item)
        print

def OpenThing(state, thing):
    roomObject = state.hero.parent.GetFirstItemByName(thing)
    if roomObject:
        if isinstance(roomObject, Container):
            roomObject.Open()
        else:
            print "I can't open that."
    else:
        print "I don't see that in the room."

def CloseThing(state, thing):
    roomObject = state.hero.parent.GetFirstItemByName(thing)
    if roomObject:
        if isinstance(roomObject, Container):
            roomObject.Close()
        else:
            print "I can't close that."
    else:
        print "I don't see that in the room."

def PickUpToolbox(state):
    toolbox = state.apartment.main.toolbox
    state.hero.Pickup(toolbox)

def GetObject(state, obj, roomObject):
    roomObject = state.hero.parent.GetFirstItemByName(roomObject)
    if roomObject:
        if isinstance(roomObject, Container):
            container = roomObject
            if container.state == Container.State.OPEN:
                thing = container.GetFirstItemByName(obj)
                if thing:
                    state.hero.Pickup(thing)
                else:
                    print "I don't see that in the {}.".format(container.name)
            else:
                print "Try opening it first."
        elif isinstance(roomObject, Surface):
            surface = roomObject
            thing = surface.GetFirstItemByName(obj)
            if thing:
                state.hero.Pickup(thing)
            else:
                print "I don't see that on the {}.".format(surface.name)
        else:
            print "How could I do that?"
    else:
        print "I don't see that in the room."

    print

def Inventory(state):
    objs = state.hero.inventory
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

    if not hero.inventory:
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

