#!/usr/bin/python3

from binascii import hexlify
from ecf import Corpus, Fuzz, ParallelTargetRunner, read_corpus_dir
import ecf.mutator as m
from ecf.target import RawTraceOutputTarget

# Use Qemu to run a bare metal ARM firmware
# that writes execution trace to UART
# using GCC instrumentation

class NullTermInputTarget:
    """The binary expects null-terminated inputs
    don't put it in the hands of mutator"""
    def __init__(self, t):
        self.target = t

    def copy(self):
        return NullTermInputTarget(self.target)

    def run(self, inp):
        return self.target.run(inp + b'\0')


t = NullTermInputTarget(
        RawTraceOutputTarget([
            'qemu-system-arm',
            '-M', 'versatilepb',
            '-m', '8M',
            '-nographic',
            '-semihosting',
            '-kernel', './example-data/arm/example.bin'],
            { 'QEMU_AUDIO_DRV' : 'none'},
            'stdout',
            address_size=4))

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
        if fuzz.stats.batch_num % 1 == 0:
            fuzz.stats.show_timings()
        if fuzz.stats.batch_num % 30 == 0:
            fuzz.stats.show_inputs(5)
