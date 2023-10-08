class Rotate:
    '''Use each mutator once then start again
    name will be set to currently used mutator'''

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

class NRotate:
    '''Use each mutator N times then start again
    i.e. NRotate((RandByte(1, 4), 3), (m.Splice(corpus), 2)) is the same as
    Rotate(RandByte(1, 4), RandByte(1, 4), RandByte(1, 4), m.Splice(corpus), m.Splice(corpus))'''

    def __init__(self, *mutators):
        self.mutators = mutators
        self.mutator_ind = 0
        self.mutator_uses_left = mutators[0][1]
        self.__update()

    def __update(self):
        m, uses = self.mutators[self.mutator_ind]
        self.name = m.name
        self.mutator_uses_left = uses

    def mutate(self, samples, n):
        if self.mutator_uses_left <= 0:
            self.mutator_ind = (self.mutator_ind + 1) % len(self.mutators)
            self.__update()

        m = self.mutators[self.mutator_ind][0]
        self.mutator_uses_left -= 1

        return m.mutate(samples, n)
