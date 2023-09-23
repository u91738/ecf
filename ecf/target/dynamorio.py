import subprocess
import os
import glob
from tempfile import TemporaryDirectory
import re

class DynamoRIOTarget:
    '''Run an executable using DynamoRIO drcov to get the trace.
    Should work with any executable. Faster than Valgrind.
    Executable takes input from stdin.
    Override run() for other ways to pass input'''

    def __init__(self, args, toolpath):
        self.playground = TemporaryDirectory(prefix='fz-dyn')
        self.tool = toolpath
        self.args = args
        self.toolargs = [
            self.tool,  '-t', 'drcov', '-dump_text',
            '-logdir', self.playground.name, '--'
        ] + args
        # module[ 19]: 0x00000000000ad991,   4
        self.module_regex = re.compile("^module\\[ *([0-9]+)\\]: *([x0-9a-fA-F]+), *[0-9]+$")

    def copy(self):
        return DynamoRIOTarget(self.args, self.tool)

    def run(self, inp):
        proc = subprocess.run(
                self.toolargs,
                input=inp,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
                )

        return proc.returncode >= 0, self._last_trace()

    def _last_trace(self):
        trace = set()
        for log_file in glob.glob(f"{self.playground.name}/*.log"):
            with open(log_file, 'r') as f:
                for line in f:
                    m = self.module_regex.search(line)
                    if m:
                        module = int(m.group(1))
                        offset = int(m.group(2), 16)
                        # set high bytes to something
                        # just to separate module spaces
                        addr = (module << (6*8)) + offset
                        trace.add(addr)
            os.unlink(log_file)
        return trace
