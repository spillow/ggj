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

class ContentsWalker:
    def GetItemsByName(self, name):
        return [x for x in self.contents if x.name == name]

    def GetFirstItemByName(self, name):
        items = self.GetItemsByName(name)
        if items:
            return items[0]
        else:
            return None

class Object(object):
    def __init__(self, name, parent):
        self.name = name
        # set if this is important for a particular object
        self.weight = 0
        self.parent = parent

    def Interact(self):
        assert 'Implement your own Interact()!'

    def __str__(self):
        return "{0}".format(self.name)

    def GetRoom(self):
        currParent = self.parent
        while not isinstance(currParent, Room):
            currParent = currParent.parent

        return currParent

class Hero(Object, ContentsWalker):
    INITIAL_FEEL = 50
    def __init__(self, startRoom):
        super(Hero, self).__init__("", startRoom)
        self.feel          = Hero.INITIAL_FEEL
        self.currBalance   = 100
        self.inventory = []

    def GetItemsByName(self, name):
        return [x for x in self.inventory if x.name == name]

    def ClearPath(self, thing):
        if not isinstance(thing.parent, Container):
            return True

        return thing.parent.state == Container.State.OPEN and \
            self.ClearPath(thing.parent)

    def Pickup(self, thing):
        if not self.parent is thing.GetRoom():
            print "I can't pick up something in a different room."
        elif not self.ClearPath(thing):
            print "Got to dig a little deeper."
        elif thing.weight > 100:
            print "I can't pick this up."
        else:
            self.inventory.append(thing)
            if isinstance(thing.parent, Container):
                thing.parent.contents.remove(thing)
            print "Got it."
        print

    def Destroy(self, thing):
        if isinstance(thing, list):
            for item in thing:
                self.inventory.remove(item)
        else:
            self.inventory.remove(thing)

    def ChangeRoom(self, room):
        # stopping logic
        self.parent = room
        for item in self.inventory:
            item.parent = room

class Container(Object, ContentsWalker):
    class State:
        OPEN   = 0
        CLOSED = 1

    def __init__(self, name, parent):
        super(Container, self).__init__(name, parent)
        self.state = Container.State.CLOSED
        self.contents = []
        self.weight = 1000 # containers are just too much

    def Open(self):
        if self.state == Container.State.OPEN:
            print "\nThe {0} is already open.".format(self.name)
        else:
            print "\nThe {0} is now open.".format(self.name)

        self.state = Container.State.OPEN

    def Close(self):
        if self.state == Container.State.CLOSED:
            print "\nThe {0} is already closed.".format(self.name)
        else:
            print "\nThe {0} is now closed.".format(self.name)

        self.state = Container.State.CLOSED

    def __str__(self):
        if self.state == Container.State.OPEN:
            if self.contents:
                descr = "an open {name}, containing:\n".format(name=self.name)
                for o in self.contents:
                    descr += "    a {name}\n".format(name=o.name)
            else:
                descr = "an open {name} with nothing in it".format(name=self.name)

            return descr.strip()
        elif self.state == Container.State.CLOSED:
            return "a {name}, it is closed".format(name=self.name)
        else:
            assert 'unknown state!'

class Surface(Object, ContentsWalker):
    def __init__(self, name, parent):
        super(Surface, self).__init__(name, parent)
        self.contents = []

class Room:
    def __init__(self, name, contents):
        self.name = name
        self.contents = contents

    def GenFields(self):
        for item in self.contents:
            setattr(self, item.name, item)

class Apartment:
    def __init__(self):
        self.main     = Room("main room", [])
        self.bedroom  = Room("bedroom", [])
        self.bathroom = Room("bathroom", [])
        self.closet   = Room("closet", [])
        self.rooms    = [self.main, self.bedroom, self.bathroom, self.closet]

        phone   = Object("phone", self.main)
        toolbox = Container("toolbox", self.main)
        fridge  = Container("fridge", self.main)
        cabinet = Container("cabinet", self.main)
        table   = Surface("table", self.main)

        self.main.contents = [phone, toolbox, fridge, cabinet, table]
        self.main.GenFields()

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

            if self.gamestate.hero.currBalance < items[choice][0]:
                emit("Insufficient funds.")
                break
            else:
                self.gamestate.hero.currBalance -= items[choice][0]
                self.ScheduleOrder(Object(choice, items[choice][1]))
                break

class GroceryNumber(StoreNumber):
    def GetStoreItems(self):
        mainroom = self.gamestate.apartment.main
        foods = {
            "spicy food" : (10, mainroom.fridge),
            "caffeine"   : (5,  mainroom.fridge),
            "bananas"    : (2,  mainroom.fridge),
            "ice cubes"  : (6,  mainroom.fridge),
        }
        return foods

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")

    def TimeWaste(self, choice):
        self.gamestate.currTime += timedelta(minutes=30)

    def FeelChange(self):
        self.gamestate.hero.feel -= 2

    def ScheduleOrder(self, choice):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.currTime + timedelta(days=1)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, tomorrow))

class HardwareNumber(StoreNumber):
    def GetStoreItems(self):
        mainroom = self.gamestate.apartment.main
        hardware = {
            "hammer"        : (20, mainroom.toolbox),
            "box of nails"  : (5,  mainroom.toolbox),
            "plywood sheet" : (30, mainroom.table),
        }
        return hardware

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the hardware store.  Hope we got what you're looking for!")

    def TimeWaste(self, choice):
        self.gamestate.currTime += timedelta(minutes=2)

    def FeelChange(self):
        self.gamestate.hero.feel -= 10

    def ScheduleOrder(self, choice):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you in a couple days.")
        twoDays = self.gamestate.currTime + timedelta(days=2)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, twoDays))

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1
    CLOSET_READY    = 2
    CLOSET_NAILED   = 3

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

        self.apartment = Apartment()
        self.hero      = Hero(self.apartment.main)
        self.alterEgo = alterego.AlterEgo()

    def SetDeliveryQueue(self, queue):
        self.deliveryQueue = queue

    def GetDateAsString(self):
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    def emit(self, s):
        print s
        print

    def STATE_BEGIN_Prompt(self):
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.GetDateAsString()))

        self.emit("In the corner you see a toolbox.")

    def prompt(self):
        # Check the 'feel' of our hero to see whether he needs to hit
        # the sack.
        if self.hero.feel <= 0:
            self.hero.feel = 0
            self.emit("I'm feeling very tired.  I'm going to pass out.....")
            for i in xrange(5):
                self.emit(".")
                time.sleep(1)
            # Now run the alterego during his sleep
            self.alterEgo.run(self)
            # Now that he is finished, reset
            self.currFSMState = GameState.BEGIN
            self.hero.feel = self.hero.INITIAL_FEEL

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

