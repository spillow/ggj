
import actions

COMMANDS = {
    "call phone" : actions.CallPhone
}

# returns a two tuple
# (ok, errorMessage)
# or
# (ok, action)
# ok whether the parse succeeded
# errorMessage on fail or action on success
def parse(userInput):
    for (command, action) in COMMANDS.iteritems():
        words = command.split()
        if all(word in userInput for word in words):
            return (True, action)

    return (False, "Don't understand command.")

    # fuzzy input from user.  Basic idea is
    # if all key words appear then accept it.
    return (False, "Can't do that!")

