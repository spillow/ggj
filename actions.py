# Action functions that a user could possibly execute.
# Actions are responsible for updating the given gamestate
# and supplying any kind of feedback with regards to not
# being able perform an action.

def prompt(s):
    return raw_input(s)

def emit(s):
    print s
    print

def CallPhone(state):
    number = prompt("What number?: ")
    if number in state.phoneNumbers:
        emit("Okay, you've called the number.")
    else:
        emit("Who's number is that?")
