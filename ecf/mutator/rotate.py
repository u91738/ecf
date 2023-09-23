from random import randrange, choice

class Rotate:
    def __init__(self, *mutators):
        self.mutators = mutators
        self.i = 0
        self.__update_name()

    def __update_name(self):
        self.name = self.mutators[self.i].name

    def mutate(self, samples, n):
        m = self.mutators[self.i]
        self.i = (self.i + 1) % len(self.mutators)
        self.__update_name()
        return m.mutate(samples, n)
