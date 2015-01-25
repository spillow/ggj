import datetime
from datetime import timedelta
import alterego
import time
import delivery

class PhoneNumber:
    def __init__(self, name, number, gamestate):
        self.name      = name
        self.number    = number
        self.gamestate = gamestate

    def __str__(self):
        return "{name}: {number}".format(name=self.name, number=self.number)

    def __eq__(self, other):
        return other == self.number

class RoomObject:
    OPEN        = 0
    CLOSED      = 1
    IN          = 2
    ON          = 3
    # defines objects within the primary room.
    # objects (i.e. toolbox) can contain other objects, or objects (i.e table)
    # can have other objects on top of them.
    def __init__(
        self,
        object_name,
        in_or_on=None,
        open_or_closed=None,
        contents=[]):

        self.name = object_name
        self.contents = list(contents)
        self.open_or_closed = open_or_closed

    def __str__(self):
        if self.open_or_closed == RoomObject.OPEN:
            if self.contents:
                descr = "an open {name}, containing:\n".format(name=self.name)
                for o in self.contents:
                    descr += "    a {name}\n".format(name=o.name)
            else:
                descr = "an open {name} with nothing in it".format(name=self.name)

            return descr.strip()
        elif self.open_or_closed == RoomObject.CLOSED:
            return "a {name}, it is closed".format(name=self.name,
                    open_or_closed=self.open_or_closed)
        else:
            return "a {name}".format(name=self.name)

class StoreNumber(PhoneNumber):
    def Interact(self):
        emit = self.gamestate.emit
        items = self.GetStoreItems()
        self.Greeting()
        maxlen = max(len(x) for (x,_) in items.iteritems())
        for (item, (cost,_)) in items.iteritems():
            print "{0}${1}.00".format(item+'.'*(maxlen-len(item))+'.........', cost)
        while True:
            choice = raw_input("> ")
            if not choice in (x for (x,_) in items.iteritems()):
                emit("We don't have that.")
                continue

            self.TimeWaste(choice)
            self.FeelChange()

            if self.gamestate.currBalance < items[choice][0]:
                emit("Insufficient funds.")
                break
            else:
                self.gamestate.currBalance -= items[choice][0]
                self.ScheduleOrder(choice, items[choice][1])
                break

class GroceryNumber(StoreNumber):
    def GetStoreItems(self):
        foods = {
            "spicy food" : (10, "fridge"),
            "caffeine"   : (5, "fridge"),
            "bananas"    : (2, "fridge"),
            "ice Cubes"  : (6, "fridge"),
        }
        return foods

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")

    def TimeWaste(self, choice):
        self.gamestate.currTime += timedelta(minutes=30)

    def FeelChange(self):
        self.gamestate.feel -= 2

    def ScheduleOrder(self, choice, whereToPut):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.currTime + timedelta(days=1)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, tomorrow, whereToPut))

class HardwareNumber(StoreNumber):
    def GetStoreItems(self):
        hardware = {
            "hammer"        : (20, "toolbox"),
            "box of nails"  : (5, "toolbox"),
            "plywood sheet" : (30, "table"),
        }
        return hardware

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the hardware store.  Hope we got what you're looking for!")

    def TimeWaste(self, choice):
        self.gamestate.currTime += timedelta(minutes=2)

    def FeelChange(self):
        self.gamestate.feel -= 10

    def ScheduleOrder(self, choice, whereToPut):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you in a couple days.")
        twoDays = self.gamestate.currTime + timedelta(days=2)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, twoDays, whereToPut))

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1
    CLOSET_READY    = 2
    CLOSET_NAILED   = 3

    INITIAL_FEEL = 50

    def __init__(self):
        self.phoneNumbers = [
            GroceryNumber("Grocery", "288-7955", self),
            HardwareNumber("Hardware Store", "592-2874", self)
        ]
        self.currFSMState = GameState.BEGIN
        # March 15, 1982 at 3:14 AM
        self.currTime = datetime.datetime(
            1982, # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute

        toolbox = RoomObject("toolbox", "in", RoomObject.CLOSED, [])
        fridge  = RoomObject("fridge", "in", RoomObject.CLOSED, [])
        table   = RoomObject("table", "on")
        cabinet = RoomObject("cabinet", "in", RoomObject.OPEN, [])

        self.mainRoomObjects = [toolbox, fridge, table, cabinet]
        self.carryingObjects = []
        self.currBalance = 100 # dollars
        self.feel = GameState.INITIAL_FEEL
        self.ownedFood = []
        self.alterEgo = alterego.AlterEgo()

    def SetDeliveryQueue(self, queue):
        self.deliveryQueue = queue

    def GetDateAsString(self):
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    def emit(self, s):
        print s
        print

    def MakeRoomObject(self, s):
        return RoomObject(s)

    def GetRoomObjects(self, name=None):
        if self.currFSMState != GameState.APARTMENT_READY:
            return []

        if name:
            return [o for o in self.mainRoomObjects if o.name==name]
        else:
            return self.mainRoomObjects

    def GetCarryingObjects(self, name=None):
        if name:
            return [o for o in self.carryingObjects if o.name==name]
        else:
            return self.carryingObjects

    def AddCarryingObjects(self, obj):
        self.carryingObjects.append(obj)

    def STATE_BEGIN_Prompt(self):
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.GetDateAsString()))

        if self.mainRoomObjects:
            self.emit("In the corner you see a toolbox.")

    def prompt(self):
        # Check the 'feel' of our hero to see whether he needs to hit
        # the sack.
        if self.feel <= 0:
            self.feel = 0
            self.emit("I'm feeling very tired.  I'm going to pass out.....")
            for i in xrange(5):
                self.emit(".")
                time.sleep(1)
            # Now run the alterego during his sleep
            self.alterEgo.run(self)
            # Now that he is finished, reset
            self.currFSMState = GameState.BEGIN
            self.feel = GameState.INITIAL_FEEL

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

