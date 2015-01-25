
import actions

COMMANDS = {
    "call phone" : actions.CallPhone,
    "rolodex" : actions.Rolodex,
    "look at watch" : actions.LookAtWatch,
    "ponder" : actions.Ponder
}

# returns a two tuple
# (ok, errorMessage)
# or
# (ok, action)
# ok whether the parse succeeded
# errorMessage on fail or action on success
def parse(userInput):
    for (command, action) in COMMANDS.iteritems():
        words = [word.lower() for word in command.split()]
        lowerInput = userInput.lower()
        if all(word in lowerInput for word in words):
            return (True, action)

    return (False, "Don't understand command.")
