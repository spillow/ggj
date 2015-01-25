# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta
from gamestate import RoomObject

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

def CallPhone(state):
    number = prompt("What number?: ")
    for phoneNumber in state.phoneNumbers:
        if number == phoneNumber.number:
            phoneNumber.Interact()
            return

    emit("Who's number is that?")

def Rolodex(state):
    for phonenumber in state.phoneNumbers:
        print phonenumber
    print

def LookAtWatch(state):
    emit("\nThe current time is {time}".format(time=state.GetDateAsString()))

def Ponder(state):
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            numHours = int(length)
            if numHours > 3:
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

def GetRoomObjects(state, name):
    return [o for o in state.roomObjects if o.name==name]


def ExamineToolbox(state):
    objs = GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")

    for o in state.roomObjects:
        if o.name == 'toolbox':
            emit("\nYou see " + str(o))

def OpenToolbox(state):
    objs = GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")
        return

    toolbox = objs[0]

    if toolbox.open_or_closed == RoomObject.OPEN:
        emit("\nThe toolbox is already open.")

    objs[0].open_or_closed = RoomObject.OPEN
    emit("\nThe toolbox is now open.")

def CloseToolbox(state):
    objs = GetRoomObjects(state, "toolbox")

    if not objs:
        emit("\nI see no toolbox here")
        return

    toolbox = objs[0]

    if toolbox.open_or_closed == RoomObject.CLOSED:
        emit("\nThe toolbox is already closed.")
        return

    objs[0].open_or_closed = RoomObject.CLOSED
    emit("\nThe toolbox is now closed.")
