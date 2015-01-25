# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

# Actions do take time so each should implement how they move
# the clock forward.

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

def CallPhone(state):
    number = prompt("What number?: ").strip()
    if number in state.phoneNumbers:
        emit("Okay, you've called the number.")
    else:
        emit("Who's number is that?")

def Rolodex(state):
    for phonenumber in state.phoneNumbers:
        print phonenumber
    print

def LookAtWatch(state):
    emit("The current time is {time}".format(time=state.GetDateAsString()))


