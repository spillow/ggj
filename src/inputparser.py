from . import actions

COMMANDS = {
    "debug items": actions.debug_items,
    "call phone": actions.call_phone,
    "rolodex": actions.rolodex,
    "look at watch": actions.look_at_watch,
    "ponder": actions.ponder,
    "balance": actions.check_balance,
    "feel": actions.check_feel,
    "eat {a}": actions.eat_thing,
    "examine {a}": actions.examine_thing,
    "watch {a}": actions.watch_tv,
    "look in {a}": actions.examine_thing,
    "open {a}": actions.open_thing,
    "close {a}": actions.close_thing,
    "pick up {a} from {b}": actions.get_object,
    "get {a} from {b}": actions.get_object,
    "inventory": actions.inventory,
    "go in {a}": actions.enter_room,
    "go to {a}": actions.enter_room,
    "enter {a}": actions.enter_room,
    "enter the {a}": actions.enter_room,
    "nail wood to exit": actions.nail_self_in,
    "nail wood to door": actions.nail_self_in,
    "nail self in": actions.nail_self_in,
    "nail self in closet": actions.nail_self_in,
    "inspect room": actions.inspect_room,
    "view room": actions.inspect_room,
    "look around room": actions.inspect_room,
    "mail check": actions.mail_check
    # ice bath
}


class PatVar:
    def __init__(self, s):
        self.s = s

    def __bool__(self):
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
    inputTokens = userInput.split()

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
    for (command, action) in COMMANDS.items():
        (ok, args) = expand(command, userInput)
        if ok:
            return (True, action, args)

    return (False, "Don't understand command.", [])
