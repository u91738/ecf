from collections import defaultdict
import pickle

class BlockStats:
    def __init__(self):
        self.inputs = set()
        self.visits = 0

    def add_input(self, inp:bytes):
        self.inputs.add(inp)
        self.visits += 1

    def trim(self, n:int):
        if len(self.inputs) > n:
            inps = list(self.inputs)
            inps.sort(key=len)
            self.inputs = set(inps[:n])

class Corpus:
    blocks: defaultdict[int, BlockStats]
    inputs: set[bytes]

    def __init__(self):
        self.blocks = defaultdict(BlockStats)
        self.inputs = set()

    def add_input(self, inp:bytes, visited_blocks:set[int]):
        assert isinstance(visited_blocks, set)
        assert isinstance(inp, bytes)

        for b in visited_blocks:
            self.blocks[b].add_input(inp)
        self.inputs.add(inp)

    def suggest_inputs(self, n):
        r = set()
        for block, st in sorted(self.blocks.items(), key=lambda x: x[1].visits): # least visited blocks
            for i in st.inputs:
                r.add(i)
                if len(r) == n:
                    return r
        return r

    def _update_inputs(self):
        self.inputs = set()
        for i in self.blocks.values():
            self.inputs |= i.inputs

    def trim(self, n):
        for i in self.blocks.values():
            i.trim(n)
        self._update_inputs()

    def dump(self, f):
        pickle.dump(self.blocks, f)

    def load(self, f):
        self.blocks = pickle.load(f)
        self._update_inputs()
