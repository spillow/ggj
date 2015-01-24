
import gamestate
import inputparser

def run():
    state = gamestate.GameState()
    while True:
        userInput = state.prompt()
        (ok, action) = inputparser.parse(userInput)
        if ok:
            (ok, errMsg) = action(state)
            if not ok:
                print errMsg
        else:
            errMsg = action
            print errMsg


