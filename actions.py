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
            if numHours > 1000: # TODO: make this shorter.
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

#def _GetToolboxItem(state, item):
#    if state.currFSMState == GameState.APARTMENT_READY:
#        if GameState.GetCarryingObjects(state, item):
#            emit("\nYou already have the %s" % item)
#            return
#        else:
#            objs = GameState.GetRoomObjects(state, "toolbox")
#            toolbox = objs[0]
#
#            if toolbox.open_or_closed == RoomObject.CLOSED:
#                emit("\nI see no %s here" % item)
#                return
#
#            emit("\nYou grab the %s from the toolbox" % item)
#
#            the_item = [obj for obj in toolbox.contents if obj.name==item][0]
#            new_contents = [obj for obj in toolbox.contents if obj.name!=item]
#            toolbox.contents = new_contents
#            GameState.AddCarryingObjects(state, the_item)
#    else:
#        if GameState.GetCarryingObjects(state, item):
#            emit("\nYou already have the %s" % item)
#            return
#        else:
#            emit("\nI see no %s here" % item)
#            return

def _GetRoomItem(state, item_name):
    if state.currFSMState == GameState.APARTMENT_READY:
        if GameState.GetCarryingObjects(state, item_name):
            emit("\nYou already have the %s" % item_name)
            return
        else:
            containers = GameState.GetRoomObjects(state)

            for container in containers:
                if container.name == 'toolbox':
                    if container.open_or_closed == RoomObject.CLOSED:
                        continue

                items = [obj for obj in container.contents if obj.name==item_name]

                if not items:
                    continue
                else:
                    emit("\nYou grab the %s from the %s" % (item_name, container.name))
                    new_contents = [obj for obj in container.contents
                            if obj.name!=item_name]
                    container.contents = new_contents
                    GameState.AddCarryingObjects(state, items[0])
                    return
    else:
        if GameState.GetCarryingObjects(state, item_name):
            emit("\nYou already have the %s" % item_name)
            return

    emit("\nI see no %s here" % item_name)
    return

def GetHammer(state):
    _GetRoomItem(state, "hammer")

def GetNails(state):
    _GetRoomItem(state, "box of nails")

def Inventory(state):
    objs = GameState.GetCarryingObjects(state)
    if not objs:
        emit("\nYou have no objects in your inventory")
        return

    print "\nYou are carrying the following:"

    for obj in objs:
        print "    ", str(obj)

    print

def _GetInventoryItem(state, item_name):
    objs = GameState.GetCarryingObjects(state)

    if not objs:
        return None

    obj = [o for o in objs if o.name==item_name]

    if not obj:
        return None

    return obj[0]

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
    _GetRoomItem(state, 'plywood sheet')

def NailSelfIn(state):
    if state.currFSMState == GameState.CLOSET_NAILED:
        emit("\nWasn't once enough?")
        return

    if state.currFSMState != GameState.CLOSET_READY:
        emit("\nThat would be very difficult from your current location")
        return

    objs = GameState.GetCarryingObjects(state)
    if not objs:
        emit("\nYou have no objects with which to do that")
        return

    hammer = _GetInventoryItem(state, 'hammer')
    nails = _GetInventoryItem(state, 'box of nails')
    plywood = _GetInventoryItem(state, 'plywood sheet')

    if not hammer or not nails or not plywood:
        if not plywood:
            s = 'Perhaps some wood?'
        if not hammer:
            s = 'Perhaps a hammer?'
        if not nails:
            s = 'Perhaps some nails?'

        emit("\nYou are missing something.  %s" % s)
        return

    new_objs = [o for o in objs if o.name not in
            ['hammer', 'box of nails', 'plywood sheet']]

    state.carryingObjects = new_objs

    emit("\nYou have successfully nailed yourself into a rather small closet.")

    state.currFSMState = GameState.CLOSET_NAILED

    numHours = 2
    state.currTime += timedelta(hours=numHours)
    state.feel -= 10 * numHours
