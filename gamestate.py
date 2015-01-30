import datetime
from datetime import timedelta
import alterego
import time
import delivery

class Object(object):
    def __init__(self, name, parent, delay=False):
        self.name = name
        # set if this is important for a particular object
        self.weight = 0
        self.parent = parent

        if not delay and parent is not None:
            self.parent.contents.append(self)

    def Interact(self):
        assert 'Implement your own Interact()!'

    def __str__(self):
        return "{0}".format(self.name)

    def GetRoom(self):
        currParent = self.parent
        while not isinstance(currParent, Room):
            currParent = currParent.parent

        return currParent

class Container(Object):
    def __init__(self, name, parent):
        super(Container, self).__init__(name, parent)
        self.contents = []
        self.weight = 1000 # containers are just too much

    def GetItemsByName(self, name):
        return [x for x in self.contents if x.name == name]

    def GetFirstItemByName(self, name):
        items = self.GetItemsByName(name)
        if items:
            return items[0]
        else:
            return None

    def GenFields(self):
        for item in self.contents:
            setattr(self, item.name, item)

class PhoneNumber:
    def __init__(self, name, number, gamestate):
        self.name      = name
        self.number    = number
        self.gamestate = gamestate

    def __str__(self):
        return "{name}: {number}".format(name=self.name, number=self.number)

    def __eq__(self, other):
        return other == self.number

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
                self.ScheduleOrder(Object(choice, items[choice][1], delay=True))
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
        self.gamestate.watch.currTime += timedelta(minutes=30)

    def FeelChange(self):
        self.gamestate.hero.feel -= 2

    def ScheduleOrder(self, choice):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.watch.currTime + timedelta(days=1)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, tomorrow))

class HardwareNumber(StoreNumber):
    def GetStoreItems(self):
        mainroom = self.gamestate.apartment.main
        hardware = {
            "hammer"        : (20, mainroom.toolbox),
            "box-of-nails"  : (5,  mainroom.toolbox),
            "plywood-sheet" : (30, mainroom.table),
        }
        return hardware

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the hardware store.  Hope we got what you're looking for!")

    def TimeWaste(self, choice):
        self.gamestate.watch.currTime += timedelta(minutes=2)

    def FeelChange(self):
        self.gamestate.hero.feel -= 10

    def ScheduleOrder(self, choice):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you in a couple days.")
        twoDays = self.gamestate.watch.currTime + timedelta(days=2)
        self.gamestate.deliveryQueue.AddOrder(
            delivery.Order(choice, twoDays))

# decorator for Interact()
def sameroom(func):
    def check(self, hero):
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            print "Must be in the same room as the {0}".format(self.name)

    return check

class Phone(Object):
    def __init__(self, gamestate, parent):
        super(Phone, self).__init__("phone", parent)
        self.gamestate = gamestate

        self.phoneNumbers = [
            GroceryNumber("Grocery", "288-7955", gamestate),
            HardwareNumber("Hardware Store", "592-2874", gamestate)
        ]

    def prompt(self, s):
        return raw_input(s)

    @sameroom
    def Rolodex(self, hero):
        for phonenumber in self.phoneNumbers:
            print phonenumber
        print

    @sameroom
    def Interact(self, hero):
        number = self.prompt("What number?: ")
        for phoneNumber in self.phoneNumbers:
            if number == phoneNumber.number:
                phoneNumber.Interact()
                return

        print "Who's number is that?"
        print

class Watch(Object):
    def __init__(self, parent):
        super(Watch, self).__init__("watch", parent)

        # March 15, 1982 at 3:14 AM
        self.currTime = datetime.datetime(
            1982, # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute

    def GetDateAsString(self):
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    @sameroom
    def Interact(self, hero):
        print "\nThe current time is {time}".format(time=self.GetDateAsString())
        print

class Hero(Container):
    INITIAL_FEEL = 50
    def __init__(self, startRoom):
        super(Hero, self).__init__("me", startRoom)
        self.feel          = Hero.INITIAL_FEEL
        self.currBalance   = 100
        self.state         = Openable.State.OPEN

    def ClearPath(self, thing):
        if self.parent == thing.parent:
            return True

        if isinstance(thing.parent, Openable):
            if thing.parent.state == Openable.State.CLOSED:
                return False

        return self.ClearPath(thing.parent)

    def Pickup(self, thing):
        if not self.GetRoom() is thing.GetRoom():
            print "I can't pick up something in a different room."
        elif not self.ClearPath(thing):
            print "Got to dig a little deeper."
        elif thing.weight > 100:
            print "I can't pick this up."
        elif thing in self.contents:
            print "Yup, already got that."
        else:
            self.contents.append(thing)
            thing.parent.contents.remove(thing)
            print "Got it."
        print

    def Destroy(self, thing):
        if isinstance(thing, list):
            for item in thing:
                if item in self.contents:
                    self.contents.remove(item)
                else:
                    print "I don't have that."
        else:
            if item in self.contents:
                self.contents.remove(thing)
            else:
                print "I don't have that."

    def ChangeRoom(self, room):
        # stopping logic
        self.parent = room

class Openable(Container):
    class State:
        OPEN   = 0
        CLOSED = 1

    def __init__(self, name, parent):
        super(Openable, self).__init__(name, parent)
        self.state = Openable.State.CLOSED

    @sameroom
    def Examine(self, hero):
        if self.state != Openable.State.OPEN:
            print "The {} must be opened first.".format(self.name)
            return

        if not self.contents:
            print "nothing in the {}.".format(self.name)
            print
        else:
            print "{} contains:".format(self.name)
            for item in self.contents:
                print "    {0}".format(item)
            print

    @sameroom
    def Open(self, hero):
        if self.state == Openable.State.OPEN:
            print "\nThe {0} is already open.".format(self.name)
        else:
            print "\nThe {0} is now open.".format(self.name)

        self.state = Openable.State.OPEN

    @sameroom    
    def Close(self, hero):
        if self.state == Openable.State.CLOSED:
            print "\nThe {0} is already closed.".format(self.name)
        else:
            print "\nThe {0} is now closed.".format(self.name)

        self.state = Openable.State.CLOSED

    def __str__(self):
        if self.state == Openable.State.OPEN:
            if self.contents:
                descr = "an open {name}, containing:\n".format(name=self.name)
                for o in self.contents:
                    descr += "    a {name}\n".format(name=o.name)
            else:
                descr = "an open {name} with nothing in it".format(name=self.name)

            return descr.strip()
        elif self.state == Openable.State.CLOSED:
            return "a {name}, it is closed".format(name=self.name)
        else:
            assert 'unknown state!'

class Room(Container):
    def __init__(self, name, parent):
        super(Room, self).__init__(name, parent)

class Apartment(Container):
    def __init__(self, gamestate):
        super(Apartment, self).__init__("apartment", None)
        self.gamestate = gamestate

        self.main     = Room("main", self)
        self.bedroom  = Room("bedroom", self)
        self.bathroom = Room("bathroom", self)
        self.closet   = Room("closet", self)
        self.GenFields()

        phone   = Phone(gamestate, self.main)
        toolbox = Openable("toolbox", self.main)
        fridge  = Openable("fridge", self.main)
        cabinet = Openable("cabinet", self.main)
        table   = Container("table", self.main)

        self.main.GenFields()

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1
    CLOSET_READY    = 2
    CLOSET_NAILED   = 3

    def __init__(self):
        self.currFSMState = GameState.BEGIN

        self.apartment = Apartment(self)
        self.hero      = Hero(self.apartment.main)
        self.alterEgo  = alterego.AlterEgo()

        self.watch = Watch(self.hero)

    def SetDeliveryQueue(self, queue):
        self.deliveryQueue = queue

    def emit(self, s):
        print s
        print

    def STATE_BEGIN_Prompt(self):
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.watch.GetDateAsString()))

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
