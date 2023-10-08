import itertools as it
import more_itertools as mit
from multiprocessing import Pool, cpu_count

def runtarget(args):
    t, inputs = args
    return [t.run(i) for i in inputs]

class ParallelTargetRunner:
    '''Run target in parallel in multiple processes
    Target must have a properly working .copy()'''

    def __init__(self, target, max_tasks=None):
        self.max_tasks = max_tasks if max_tasks else cpu_count()
        self.targets = [target] # code is a bit weird because we want one target obj per process
        for _ in range(self.max_tasks - 1):
            self.targets.append(target.copy())

    def __enter__(self):
        self.pool = Pool(self.max_tasks)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.__exit__(exc_type, exc_val, exc_tb)

    def run(self, inputs):
        args = [(t, list(inps)) for t, inps in zip(self.targets, mit.divide(self.max_tasks, inputs))]
        res = self.pool.map(runtarget, args)
        return list(it.chain.from_iterable(res))

class SequentialTargetRunner:
    '''Run target sequentially for each sample'''

    def __init__(self, target):
        self.target = target

    def run(self, inputs):
        return [self.target.run(i) for i in inputs]
