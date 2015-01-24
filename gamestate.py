
class GameState:
    def __init__(self):
        pass

    # state machine

    def prompt(self):
        userInput = raw_input("What do we do next?: ")
        return userInput

