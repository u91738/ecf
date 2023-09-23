import subprocess
import os
import glob
from tempfile import TemporaryDirectory

class ValgrindTarget:
    '''Run an executable using valgrind to get trace.
    Should work with any executable. It is really slow.
    Executable takes input from stdin.
    Override run() for other ways to pass input'''

    def __init__(self, args, interval_size):
        self.playground = TemporaryDirectory(prefix='fz-valgrind')
        self.args = args
        self.interval_size = interval_size
        self.valgrind_args = [
            'valgrind',
            '--tool=exp-bbv',
            f'--bb-out-file={self.playground.name}/bb',
            f'--interval-size={self.interval_size}'
        ] + args

    def copy(self):
        return ValgrindTarget(self.args, self.interval_size)

    def run(self, inp):
        proc = subprocess.run(
                self.valgrind_args,
                input=inp,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)

        return proc.returncode >= 0, self._last_trace()

    def _last_trace(self):
        trace = set()
        for pc_file in glob.glob(f"{self.playground.name}/bb*"):
            with open(pc_file, 'r') as f:
                for line in f:
                    if line.startswith('T'):
                        for i in line[1:].split():
                            trace.add(int(i.split(':', 2)[1]))
        return trace
