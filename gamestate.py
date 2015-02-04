import datetime
from datetime import timedelta
import alterego
import time
import delivery

# decorator for Interact()
def sameroom(func):
    def check(self, hero):
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            print "Must be in the same room as the {0}".format(self.name)

    return check

class Object(object):
    def __init__(self, name, parent):
        self.name = name
        # set if this is important for a particular object
        self.weight = 0
        self.parent = parent

        if parent is not None:
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

class Food(Object):
    def __init__(self, name, parent, feelBoost):
        super(Food, self).__init__(name, parent)
        self.feelBoost = feelBoost

    def Eat(self, hero):
        hero.Pickup(self)
        hero.Destroy([self])
        hero.feel += self.feelBoost
        watch = hero.GetFirstItemByName('watch')
        watch.currTime += timedelta(minutes=20)

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

    @sameroom
    def Examine(self, hero):
        if not self.contents:
            print "nothing to see for the {}".format(self.name)
            print
        else:
            print "{} contains:".format(self.name)
            for item in self.contents:
                print "    {0}".format(item)
            print

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
        for (item, cost) in items.iteritems():
            print "{0}${1}.00".format(item+'.'*(maxlen-len(item))+'.........', cost)
        while True:
            choice = raw_input("> ")
            if not choice in (x for (x,_) in items.iteritems()):
                emit("We don't have that.")
                continue

            self.TimeWaste(choice)
            self.FeelChange()

            if self.gamestate.hero.currBalance < items[choice]:
                emit("Insufficient funds.")
                break
            else:
                self.gamestate.hero.currBalance -= items[choice]
                self.ScheduleOrder(choice)
                break

class GroceryNumber(StoreNumber):
    def GetStoreItems(self):
        mainroom = self.gamestate.apartment.main
        foods = {
            "spicy-food" : 10,
            "caffeine"   : 5,
            "bananas"    : 2,
            "ice-cubes"  : 6
        }
        return foods

    def Greeting(self):
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")

    def TimeWaste(self, choice):
        self.gamestate.watch.currTime += timedelta(minutes=30)

    def FeelChange(self):
        self.gamestate.hero.feel -= 2

    def FoodFeel(self):
        feel = {
            "spicy-food" : 30,
            "caffeine"   : 20,
            "bananas"    : 5,
            "ice-cubes"  : 2
        }
        return feel

    def ScheduleOrder(self, choice):
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.watch.currTime + timedelta(days=1)
        def purchase(a, b):
            Food(choice, self.gamestate.apartment.main.fridge,
                 self.FoodFeel()[choice])
            print "Food truck order has arrived!"
        self.gamestate.eventQueue.AddEvent(purchase, tomorrow)

class HardwareNumber(StoreNumber):
    def GetStoreItems(self):
        mainroom = self.gamestate.apartment.main
        hardware = {
            "hammer"        : 20,
            "box-of-nails"  : 5,
            "plywood-sheet" : 30
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
        def purchase(a, b):
            if choice == 'plywood-sheet':
                location = self.gamestate.apartment.main.table
            else:
                location = self.gamestate.apartment.main.toolbox

            Object(choice, location)
        self.gamestate.eventQueue.AddEvent(purchase, twoDays)

class SuperNumber(PhoneNumber):
    def Interact(self):
        print "Calling the super..."
        for i in xrange(3):
            print "ring..."
            time.sleep(1)

        print "Okay, doesn't look like anybody is answering."

        self.gamestate.hero.feel -= 30
        self.gamestate.watch.currTime += timedelta(minutes=20)

class TV(Object):
    def __init__(self, parent):
        super(TV, self).__init__("tv", parent)

    @sameroom
    def Examine(self, hero):
        print "You turn on the tv."
        print
        print """Breaking news: prominent astrophysicists have recently
discovered a strange anomaly in space.  The origins are not yet clear.
Stay tuned for further details."""

class Phone(Object):
    def __init__(self, gamestate, parent):
        super(Phone, self).__init__("phone", parent)
        self.gamestate = gamestate

        self.phoneNumbers = [
            GroceryNumber("Grocery", "288-7955", gamestate),
            HardwareNumber("Hardware Store", "592-2874", gamestate),
            SuperNumber("The Super", "198-2888", gamestate)
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

    def isOpen(self):
        return self.state == Openable.State.OPEN

    def isClosed(self):
        return self.state == Openable.State.CLOSED

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

    def Leave(self, hero):
        return True

    def Enter(self, fromRoom, hero):
        if fromRoom.Leave(hero):
            hero.ChangeRoom(self)
            print "You are now in the {}".format(self.name)

class Closet(Room):
    CLOSET_READY    = 0
    CLOSET_NAILED   = 1

    def __init__(self, name, parent):
        super(Closet, self).__init__(name, parent)
        self.state = Closet.CLOSET_READY

    def Leave(self, hero):
        if self.state == Closet.CLOSET_NAILED:
            print "\nPerhaps you should ponder exactly how you'll do that?"
            return False
        elif self.state == Closet.CLOSET_READY:
            return True
        else:
            assert 'unknown closet state!'

class Apartment(Container):
    def __init__(self, gamestate):
        super(Apartment, self).__init__("apartment", None)
        self.gamestate = gamestate

        self.main     = Room("main", self)
        self.bedroom  = Room("bedroom", self)
        self.bathroom = Room("bathroom", self)
        self.closet   = Closet("closet", self)
        self.GenFields()

        phone   = Phone(gamestate, self.main)
        toolbox = Openable("toolbox", self.main)
        fridge  = Openable("fridge", self.main)
        cabinet = Openable("cabinet", self.main)
        table   = Container("table", self.main)
        tv      = TV(self.main)

        self.main.GenFields()

class GameState:
    BEGIN           = 0
    APARTMENT_READY = 1

    def __init__(self):
        self.apartment = Apartment(self)
        self.hero      = Hero(self.apartment.main)
        self.alterEgo  = alterego.AlterEgo()

        self.watch = Watch(self.hero)

    def SetEventQueue(self, queue):
        self.eventQueue = queue

    def emit(self, s):
        print s
        print

    def IntroPrompt(self):
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.watch.GetDateAsString()))

        self.emit("In the corner you see a toolbox.")

    def Examine(self):
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
            self.hero.feel = self.hero.INITIAL_FEEL
            self.IntroPrompt()

    def prompt(self):
        userInput = raw_input("What do we do next?: ")
        return userInput
