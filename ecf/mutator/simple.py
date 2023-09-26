from random import randrange, choice, shuffle
import more_itertools as mit

def batch(mutate_one):
    def mutate(self, samples, n):
        r = []
        while True:
            for i in samples:
                r.append(mutate_one(self, i))
                if len(r) == n:
                    return r
    return mutate

def randrange_s(lo, hi):
    return lo if lo == hi else randrange(lo, hi)

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
            pos = randrange_s(0, len(r))
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
            pos = randrange_s(0, len(r) - 1)
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
        pos = randrange_s(0, len(r) - size + 1)
        r[pos:pos] = r[pos:pos+size]
        return r

class Splice:
    def __init__(self, corpus=None, n_min=0, n_max=0xFFFF):
        self.n_min = n_min
        self.n_max = n_max
        self.corpus = corpus
        self.name = type(self).__name__

    def mutate(self, samples, n):
        inputs = list(mit.sample(self.corpus.inputs, n) if self.corpus else samples)
        r = []
        while len(r) < n:
            for a in samples:
                b = choice(inputs)
                n_max = min(self.n_max, len(a), len(b))
                n_min = min(self.n_min, len(a), len(b))
                n = randrange_s(n_min, n_max)
                r.append(a[:n] + b[n:] if randrange(0, 2) else b[:n] + a[n:])
        return r
