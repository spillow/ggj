# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from gamestate import RoomObject, GameState

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

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
            if numHours > 100: # TODO: make this shorter.
                emit("\nThat's too long to sit and do nothing.")
                continue
            else:
                break
        else:
            emit("\nWhat? Give me a number.")

    state.currTime += timedelta(hours=numHours)
    state.feel -= 10 * numHours

def CheckBalance(state):
    emit("Current Balance: ${0}".format(state.currBalance))

def CheckFeel(state):
    feel = state.feel
    if feel >= 40:
        emit("Feeling good")
    elif feel >= 20:
        emit("Feeling okay")
    else:
        emit("I'm about to hit the sheets!")


def ExamineToolbox(state):
    objs = GameState.GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")
        return

    for o in state.mainRoomObjects:
        if o.name == 'toolbox':
            emit("\nYou see " + str(o))

def OpenToolbox(state):
    objs = GameState.GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")
        return

    toolbox = objs[0]

    if toolbox.open_or_closed == RoomObject.OPEN:
        emit("\nThe toolbox is already open.")
        return

    objs[0].open_or_closed = RoomObject.OPEN
    emit("\nThe toolbox is now open.")

def CloseToolbox(state):
    objs = GameState.GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")
        return

    toolbox = objs[0]

    if toolbox.open_or_closed == RoomObject.CLOSED:
        emit("\nThe toolbox is already closed.")
        return

    objs[0].open_or_closed = RoomObject.CLOSED
    emit("\nThe toolbox is now closed.")

def PickUpToolbox(state):
    emit("\nThe toolbox is to heavy to carry")
    return

def _GetToolboxItem(state, item):
    if state.currFSMState == GameState.APARTMENT_READY:
        if GameState.GetCarryingObjects(state, item):
            emit("\nYou already have the %s" % item)
            return
        else:
            objs = GameState.GetRoomObjects(state, "toolbox")
            toolbox = objs[0]

            if toolbox.open_or_closed == RoomObject.CLOSED:
                emit("\nI see no %s here" % item)
                return

            emit("\nYou grab the %s from the toolbox" % item)

            the_item = [obj for obj in toolbox.contents if obj.name==item][0]
            new_contents = [obj for obj in toolbox.contents if obj.name!=item]
            toolbox.contents = new_contents
            GameState.AddCarryingObjects(state, the_item)
    else:
        if GameState.GetCarryingObjects(state, item):
            emit("\nYou already have the %s" % item)
            return
        else:
            emit("\nI see no %s here" % item)
            return

def GetHammer(state):
    _GetToolboxItem(state, "hammer")

def GetNails(state):
    _GetToolboxItem(state, "box of nails")

def Inventory(state):
    objs = GameState.GetCarryingObjects(state)
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print "\nYou are carrying the following:"

    for obj in objs:
        print "    ", str(obj)

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
    return

def LeaveCloset(state):
    if state.currFSMState != GameState.CLOSET_READY:
        emit("\nThat would be very difficult from your current location")
        return

    if state.currFSMState == GameState.CLOSET_READY:
        emit("\nYou have left the closet and are now back in your apartment's main room");
        state.currFSMState = GameState.APARTMENT_READY
        return
