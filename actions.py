# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

from datetime import timedelta

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
    emit("The current time is {time}".format(time=state.GetDateAsString()))

def Ponder(state):
    while True:
        length = prompt("How many hours?: ")
        if length.isdigit():
            numHours = int(length)
            if numHours > 3:
                emit("That's too long to sit and do nothing.")
                continue
            else:
                break
        else:
            emit("What? Give me a number.")

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

