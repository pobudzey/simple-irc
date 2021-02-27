import abc


class Publisher:
    def __init__(self):
        self.subscribers = list()

    def add_subscriber(self, s):
        self.subscribers.append(s)

    def rm_subscriber(self, s):
        try:
            self.subscribers.remove(s)
        except ValueError:
            # not present
            pass

    def notify(self, msg):
        for s in self.subscribers:
            if hasattr(s, "update"):
                s.update(msg)


class Subscriber:
    @abc.abstractmethod
    def update(self, msg):
        pass
