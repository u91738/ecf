#!/usr/bin/python3

from binascii import hexlify
from ecf import Corpus, Fuzz, ParallelTargetRunner, read_corpus_dir
import ecf.mutator as m
from ecf.target import GCovTarget

# Example of fuzzing a binary instrumented with gcov
# saves fuzzer state when interrupted with ctrl+C
# it is perfectly fine to load same state with different mutators, but not different targets

t = GCovTarget(['./example-data/example-gcov'], ['./example-data/example-gcov-cJSON.gcno', './example-data/example-gcov-test.gcno'])

initial_corpus = read_corpus_dir('./example-data/corpus')
corpus = Corpus()
mut = m.NRotate(
    (m.RandByte(1, 4), 5),
    (m.MarkovChainDict(corpus, 0.2), 1))

state_path = 'fuzzer_state.pickle'
try:
    with open(state_path, 'rb') as f:
        corpus.load(f)
    print('State loaded from', state_path)
except FileNotFoundError:
    pass

with ParallelTargetRunner(t) as runner:
    fuzz = Fuzz(runner, mut, initial_corpus, 1000, corpus)
    try:
        while True:
            crashes = fuzz.step()
            for c in crashes:
                print('crash found with input: ', hexlify(c))
                break

            fuzz.stats.show()
            if fuzz.stats.batch_num % 1 == 0:
                fuzz.stats.show_timings()
            if fuzz.stats.batch_num % 30 == 0:
                fuzz.stats.show_inputs(5)
    except KeyboardInterrupt:
        with open('fuzzer_state.pickle', 'wb') as f:
            fuzz.corpus.dump(f)
        print('State saved to', state_path)
