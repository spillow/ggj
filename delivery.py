class EventQueue:
    def __init__(self, state):
        self.queue = []
        self.state = state

    def AddEvent(self, action, timeToFire):
        self.queue.append((action, timeToFire))

    def Examine(self):
        toFire = [(action, time) for (action, time) in self.queue if
            self.state.watch.currTime >= time]

        rem = [(action, time) for (action, time) in self.queue if
            self.state.watch.currTime < time]

        self.queue = rem

        for (action, time) in toFire:
            action(self.state.watch.currTime, time)
