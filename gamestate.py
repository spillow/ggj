
class PhoneNumber:
    def __init__(self, name, number):
        self.name   = name
        self.number = number

    def __str__(self):
        return "{name}: {number}".format(name=self.name, number=self.number)

    def __eq__(self, other):
        return other == self.number

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1

    def __init__(self):
        self.phoneNumbers = [PhoneNumber("Grocery", "288-7955")]
        self.currFSMState = GameState.BEGIN

    def emit(self, s):
        print s
        print

    def STATE_BEGIN_Prompt(self):
        self.emit("You wake up in your apartment.")

    # state machine

    def prompt(self):
        if self.currFSMState == GameState.BEGIN:
            self.STATE_BEGIN_Prompt()
            # only printed at the beginning of the game
            self.currFSMState = GameState.APARTMENT_READY
        elif self.currFSMState == GameState.APARTMENT_READY:
            pass
        else:
            assert "Unknown game state!"

        userInput = raw_input("What do we do next?: ")
        return userInput

