import time
from datetime import datetime
import psutil
import more_itertools as mit

class Stats:
    def __init__(self, batch_size, mut, corpus):
        self.t_step_start = 0
        self.t_jobs_start = 0
        self.t_post_start = 0
        self.t_post_end = 0
        self.batch_num = 0
        self.corpus = corpus
        self.mut = mut
        self.mut_name = mut.name
        self.new_blocks_count = 0
        self.blocks_count = len(self.corpus.blocks)
        self.batch_size = batch_size

    def batch_start(self):
        self.t_step_start = time.time_ns()
        self.mut_name = self.mut.name

    def jobs_start(self):
        self.t_jobs_start = time.time_ns()

    def jobs_done(self):
        self.t_post_start = time.time_ns()

    def batch_done(self):
        self.t_post_end = time.time_ns()
        n = len(self.corpus.blocks)
        self.new_blocks_count = n - self.blocks_count
        self.blocks_count = n
        self.batch_num += 1

    def show(self):
        mem_used = psutil.Process().memory_info().rss
        print('{} Inputs tried: {:8d} BBVs found: {:4d} Mem: {:4.2f} Gib Mut: {:16} {}'.format(
                datetime.now().strftime('%H:%M:%S'),
                self.batch_num * self.batch_size,
                len(self.corpus.blocks),
                mem_used / 1024 / 1024 / 1024,
                self.mut_name,
                f'+{self.new_blocks_count}' if self.new_blocks_count else ''))

    def show_timings(self):
        print("Mutation: {:4.2f}s Jobs: {:4.2f}s Post: {:4.2f}s".format(
                (self.t_jobs_start - self.t_step_start)/10**9,
                (self.t_post_start - self.t_jobs_start)/10**9,
                (self.t_post_end - self.t_post_start)/10**9))

    def show_inputs(self, n):
        print('Input examples:')
        for v in mit.sample(self.corpus.inputs, n):
            print(v)
