import subprocess
import os
from os import path
import glob
import json
from tempfile import TemporaryDirectory
import hashlib

class GCovTarget:
    '''Run an executable instrumented with gcov (gcc -ftest-coverage -fprofile-arcs ...)
    Executable takes input from stdin.
    Override run() for other ways to pass input.
    Thousands of times faster than Valgrind target.'''

    def __init__(self, args, gcno_files):
        self.gcno_files = gcno_files
        self.playground = TemporaryDirectory(prefix='fz-gcov')
        for gcno in gcno_files: # put gcno near gcda because gcov said so
            f = path.abspath(gcno)
            ln = f"{self.playground.name}/{path.basename(gcno)}"
            os.symlink(f, ln)

        self.args = args
        self.env = os.environ | {
            'GCOV_PREFIX' : self.playground.name,
            'GCOV_PREFIX_STRIP' : "100"
        }

    def copy(self):
        return GCovTarget(self.args, self.gcno_files)

    def run(self, inp):
        p = subprocess.run(self.args,
                           input=inp,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           env=self.env)
        return p.returncode >= 0, self._last_trace()

    def _position_to_int(self, filename, line):
        hash_input = (filename + ':' + str(line)).encode('ascii', errors='ignore')
        h = hashlib.sha256(hash_input).digest()
        return int.from_bytes(h[:8], 'little')


    def _last_trace(self):
        trace = set()
        for gcda in glob.glob(f"{self.playground.name}/*.gcda"):
            p = subprocess.run(['gcov',
                                '--all-blocks',
                                '--json-format',
                                '--stdout',
                                '--object-directory', self.playground.name,
                                gcda
                                ], capture_output=True)
            cov = json.loads(p.stdout)

            for covfile in cov['files']:
                fname = covfile['file']
                for line in covfile['lines']:
                    if line['count'] > 0:
                        lno = line['line_number']
                        trace.add(self._position_to_int(fname, lno))
            os.unlink(gcda)
        return trace
