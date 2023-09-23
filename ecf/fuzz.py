import more_itertools as mit
from .corpus import Corpus
from .stats import Stats

class Fuzz:
    def __init__(self, target_runner, mutator, initial_corpus, batch_size, corpus=None):
        self.corpus = corpus if corpus else Corpus()
        self.stats = Stats(batch_size, mutator, self.corpus)
        self.runner = target_runner
        self.batch_size = batch_size
        self.mutator = mutator

        res = self.runner.run(initial_corpus)
        for sample, (success, trace) in zip(initial_corpus, res):
            assert success, "Initial sample caused crash"
            assert len(trace) > 0, "Trace failed"
            self.corpus.add_input(sample, trace)

        assert len(initial_corpus) == 1 or \
            len(set(frozenset(t) for _, t in res)) > 1,\
            "All traces are the same. Tracing is probably bugged or input is extra boring"

    def step(self):
        self.stats.batch_start()

        inputs = self.mutator.mutate(
                    self.corpus.suggest_inputs(self.batch_size),
                    self.batch_size)

        self.stats.jobs_start()
        res = self.runner.run(inputs)
        self.stats.jobs_done()

        crashes = []
        for inp, (success, trace) in zip(inputs, res):
            if success:
                self.corpus.add_input(bytes(inp), trace)
            else:
                crashes.append(inp)

        if self.stats.batch_num % 10 == 0:
            self.corpus.trim(self.batch_size * 2)

        self.stats.batch_done()
        return crashes
