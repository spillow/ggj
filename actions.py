# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from gamestate import GameState, Container, Object

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

def DebugItems(state):
    # Give me a few things to play with

    hammer  = Object("hammer", state.apartment.main)
    nails   = Object("box of nails", state.apartment.main)
    plywood = Object("plywood sheet", state.apartment.main)

    state.hero.Pickup(hammer)
    state.hero.Pickup(nails)
    state.hero.Pickup(plywood)

def CallPhone(state):
    if state.currFSMState == GameState.APARTMENT_READY:
        number = prompt("What number?: ")
        for phoneNumber in state.phoneNumbers:
            if number == phoneNumber.number:
                phoneNumber.Interact()
                return

        emit("Who's number is that?")
    else:
        emit("Not in a position to make a phone call.")

def Rolodex(state):
    if state.currFSMState == GameState.APARTMENT_READY:
        for phonenumber in state.phoneNumbers:
            print phonenumber
        print
    else:
        emit("Can't check the rolodex.")

def LookAtWatch(state):
    emit("\nThe current time is {time}".format(time=state.GetDateAsString()))

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

    state.currTime += timedelta(hours=numHours)
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

def OpenToolbox(state):
    toolbox = state.apartment.main.toolbox
    toolbox.Open()

def CloseToolbox(state):
    toolbox = state.apartment.main.toolbox
    toolbox.Close()

def PickUpToolbox(state):
    toolbox = state.apartment.main.toolbox
    state.hero.Pickup(toolbox)

def GetHammer(state):
    toolbox = state.apartment.main.toolbox
    item = toolbox.GetFirstItemByName("hammer")
    if item:
        state.hero.Pickup(item)
    else:
        print "No hammer in the toolbox."

def GetNails(state):
    toolbox = state.apartment.main.toolbox
    item = toolbox.GetFirstItemByName("box of nails")
    if item:
        state.hero.Pickup(item)
    else:
        print "No nails in the toolbox."

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

def GetWood(state):
    table = state.apartment.main.table
    item = table.GetFirstItemByName("plywood sheet")
    if item:
        state.hero.Pickup(item)

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
    nails   = hero.GetFirstItemByName('box of nails')
    plywood = hero.GetFirstItemByName('plywood sheet')

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
    state.currTime += timedelta(hours=numHours)
    hero.feel -= 10 * numHours

