#!/usr/bin/python3

import angr
from angr.project import Project
from angr.engines.failure import SimEngineFailure
from angr.engines.hook import HooksMixin
from angr.engines.vex import HeavyResilienceMixin, HeavyVEXMixin
from angr.engines.unicorn import SimEngineUnicorn

import claripy
import logging

from ecf import Corpus, Fuzz, ParallelTargetRunner, read_corpus_dir
import ecf.mutator as m
from ecf.target import AngrTarget

# Use angr to fuzz bare metal binary
# Only useful if you can't handle the state explosion with angr
# And can't recompile it for QEMU (no sources or HW not supported by QEMU)

class Engine(SimEngineFailure, HooksMixin, HeavyResilienceMixin, HeavyVEXMixin, SimEngineUnicorn):
    pass

class Target(AngrTarget):
    def get_state(self, inp):
        data = claripy.BVV(inp)
        start_state = self.project.factory.call_state(
                        self.project.loader.find_symbol('process_data').rebased_addr,
                        self.project.factory.callable.PointerWrapper(data, buffer=True), data.size() // 8,
                        prototype='void process_data(char *d, size_t d_size)',
                        add_options=angr.options.unicorn)
        return start_state

print('Load binary')
logging.getLogger('angr').setLevel('ERROR')
proj = Project('example-data/arm/example_unsanitary.elf', engine=Engine, load_options={'auto_load_libs': False})

print('Make CFG')
cfg = proj.analyses.CFGEmulated()

hooked = []
for sim_name, f in angr.SIM_PROCEDURES['libc'].items():
    for name in sim_name, '_' + sim_name:
        if name in proj.kb.functions:
            hooked.append(name)
            proj.hook_symbol(name, f())
print('Hooked', ', '.join(hooked))

print('Start fuzzing')
t = Target(proj)

initial_corpus = read_corpus_dir('./example-data/corpus')
mut = m.Rotate(m.Dup(1, 20), m.ValueInsert(4, 8), m.RandByte(1, 4), m.BitFlip(1, 4))

with ParallelTargetRunner(t) as runner:
    fuzz = Fuzz(runner, mut, initial_corpus, 1000)
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
