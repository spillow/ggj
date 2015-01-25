
import actions

COMMANDS = {
    "call phone" : actions.CallPhone,
    "rolodex" : actions.Rolodex,
    "look at watch" : actions.LookAtWatch,
    "ponder" : actions.Ponder,
    "balance" : actions.CheckBalance,
    "feel" : actions.CheckFeel,
    "examine toolbox" : actions.ExamineToolbox,
    "look in toolbox" : actions.ExamineToolbox,
    "open toolbox" : actions.OpenToolbox,
    "close toolbox" : actions.CloseToolbox,
    "pick up toolbox" : actions.PickUpToolbox,
    "get hammer" : actions.GetHammer,
    "get nails" : actions.GetNails,
    "get box of nails" : actions.GetNails,
    "inventory" : actions.Inventory,
    "go in closet" : actions.EnterCloset,
    "enter closet" : actions.EnterCloset,
    "enter the closet" : actions.EnterCloset,
    "leave closet" : actions.LeaveCloset,
    "exit closet" : actions.LeaveCloset,
    "get wood" : actions.GetWood,
    "nail wood to exit" : actions.NailSelfIn,
    "nail wood to door" : actions.NailSelfIn,
    "nail self in" : actions.NailSelfIn,
    "nail self in closet" : actions.NailSelfIn,
    # examine room
    # ice bath
    # watch television

    # examine checks
    # mail checks
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
