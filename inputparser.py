
import actions

COMMANDS = {
    "debug items"         : actions.DebugItems,
    "call phone"          : actions.CallPhone,
    "rolodex"             : actions.Rolodex,
    "look at watch"       : actions.LookAtWatch,
    "ponder"              : actions.Ponder,
    "balance"             : actions.CheckBalance,
    "feel"                : actions.CheckFeel,
    "examine {a}"         : actions.ExamineThing,
    "look in {a}"         : actions.ExamineThing,
    "open {a}"            : actions.OpenThing,
    "close {a}"           : actions.CloseThing,
    "pick up {a} from {b}": actions.GetObject,
    "get {a} from {b}"    : actions.GetObject,
    "inventory"           : actions.Inventory,
    "go in closet"        : actions.EnterCloset,
    "enter closet"        : actions.EnterCloset,
    "enter the closet"    : actions.EnterCloset,
    "leave closet"        : actions.LeaveCloset,
    "exit closet"         : actions.LeaveCloset,
    "nail wood to exit"   : actions.NailSelfIn,
    "nail wood to door"   : actions.NailSelfIn,
    "nail self in"        : actions.NailSelfIn,
    "nail self in closet" : actions.NailSelfIn,
    # examine room
    # ice bath
    # watch television

    # examine checks
    # mail checks
}

class PatVar:
    def __init__(self, s):
        self.s = s

    def __nonzero__(self):
        return self.s and self.s[0] == '{' and self.s[-1] == '}'

def unify(commandTokens, inputTokens):
    bindings = []
    for (ct, it) in zip(commandTokens, inputTokens):
        if PatVar(ct):
            bindings.append(it)
        elif ct != it:
            return (False, [])

    return (True, bindings)

def expand(command, userInput):
    commandTokens = command.split()
    inputTokens   = userInput.split()

    if len(commandTokens) != len(inputTokens):
        return (False, [])

    return unify(commandTokens, inputTokens)

# returns a two tuple
# (ok, errorMessage)
# or
# (ok, action)
# ok whether the parse succeeded
# errorMessage on fail or action on success
def parse(userInput):
    for (command, action) in COMMANDS.iteritems():
        (ok, args) = expand(command, userInput)
        if ok:
            return (True, action, args)

    return (False, "Don't understand command.", [])
