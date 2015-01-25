import datetime

class PhoneNumber:
    def __init__(self, name, number, gamestate):
        self.name      = name
        self.number    = number
        self.gamestate = gamestate

    def __str__(self):
        return "{name}: {number}".format(name=self.name, number=self.number)

    def __eq__(self, other):
        return other == self.number

class GroceryNumber(PhoneNumber):
    def Interact(self):
        foods = {
            "Spicy food" : 10,
            "Caffeine"   : 5,
            "Bananas"    : 2
        }
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")
        maxlen = max(len(x) for (x,_) in foods.iteritems())
        for (food, cost) in foods.iteritems():
            print "{0}${1}.00".format(food+'.'*(maxlen-len(food))+'.........', cost)
        while True:
            choice = raw_input("> ")
            if not choice in (x for (x,_) in foods.iteritems()):
                emit("We don't have that.")
                continue

            if self.gamestate.currBalance < foods[choice]:
                emit("Insufficient funds.")
                break
            else:
                emit("Thanks!")
                break

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1

    def __init__(self):
        self.phoneNumbers = [GroceryNumber("Grocery", "288-7955", self)]
        self.currFSMState = GameState.BEGIN
        # March 15, 1982 at 3:14 AM
        self.currTime = datetime.datetime(
            1982, # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute
        self.currBalance = 100 # dollars
        self.feel = 50
        self.ownedFood = []

    def GetDateAsString(self):
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    def emit(self, s):
        print s
        print

    def STATE_BEGIN_Prompt(self):
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.GetDateAsString()))

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

