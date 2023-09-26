#!/usr/bin/python3

from binascii import hexlify
from ecf import Corpus, Fuzz, ParallelTargetRunner, read_corpus_dir
import ecf.mutator as m
from ecf.target import GCovTarget

t = GCovTarget(['./example-data/example-gcov'], ['./example-data/example-gcov-cJSON.gcno', './example-data/example-gcov-test.gcno'])

initial_corpus = read_corpus_dir('./example-data/corpus')
corpus = Corpus()
mut = m.Rotate(
    m.RandByte(1, 4),
    m.Splice(corpus),
    m.MarkovChain(None, 0.2))

with ParallelTargetRunner(t) as runner:
    fuzz = Fuzz(runner, mut, initial_corpus, 1000, corpus)
    while True:
        crashes = fuzz.step()
        for c in crashes:
            print('crash found with input: ', hexlify(c))
            break

        fuzz.stats.show()
        if fuzz.stats.batch_num % 5 == 0:
            fuzz.stats.show_timings()
        if fuzz.stats.batch_num % 30 == 0:
            fuzz.stats.show_inputs(5)
