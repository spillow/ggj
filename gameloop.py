
import gamestate
import inputparser

def run():
    state = gamestate.GameState()
    while True:
        userInput = state.prompt()
        (ok, action) = inputparser.parse(userInput)
        if ok:
            action(state)
        else:
            errMsg = action
            print errMsg
            print


