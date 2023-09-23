from random import randrange, choice

def batch(mutate_one):
    def mutate(self, samples, n):
        r = []
        while True:
            for i in samples:
                r.append(mutate_one(self, i))
                if len(r) == n:
                    return r
    return mutate

class BitFlip:
    def __init__(self, n_min, n_max):
        self.n_min = n_min
        self.n_max = n_max
        self.name = type(self).__name__

    @batch
    def mutate(self, sample):
        r = bytearray(sample)
        cnt = randrange(self.n_min, self.n_max)
        for _ in range(cnt):
            pos = randrange(0, len(r))
            bit = randrange(0, 8)
            r[pos] ^= 1 << bit
        return r

class RandByte:
    def __init__(self, n_min, n_max):
        self.n_min = n_min
        self.n_max = n_max
        self.name = type(self).__name__

    @batch
    def mutate(self, sample):
        r = bytearray(sample)
        cnt = randrange(self.n_min, self.n_max)
        for _ in range(cnt):
            pos = randrange(0, len(r))
            v = randrange(0, 0x100)
            if randrange(0, 2):
                r.insert(pos, v)
            else:
                r[pos] = v
        return r

class ValueInsert:
    def __init__(self, n_min, n_max, values = (
                                        b'(', b')', b'[', b']', b'{', b'}',
                                        b'<', b'>',
                                        b'\\', b'.', b':', b'/', b'@', b'$',
                                        b'-', b'&', b'=', b'+',
                                        b' ', b'\n', b'\r',
                                        b'0', b'a', b's', b'A', b'S',
                                        b'\0', b'\1' b'\2' b'\3')
    ):
        self.values = values
        self.n_min = n_min
        self.n_max = n_max
        self.name = type(self).__name__

    @batch
    def mutate(self, sample):
        r = bytearray(sample)
        cnt = randrange(self.n_min, self.n_max)
        for _ in range(cnt):
            pos = randrange(0, len(r) - 1)
            r[pos:pos] = choice(self.values)
        return r

class Dup:
    def __init__(self, n_min, n_max):
        self.n_min = n_min
        self.n_max = n_max
        self.name = type(self).__name__

    @batch
    def mutate(self, sample):
        r = bytearray(sample)
        size = min(randrange(self.n_min, self.n_max), len(r))
        pos = randrange(0, len(r) - size + 1)
        r[pos:pos] = r[pos:pos+size]
        return r
