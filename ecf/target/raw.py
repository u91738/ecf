import subprocess
import more_itertools as mit

class RawTraceOutputTarget:
    '''Run an executable that writes it's trace to stdout or stderr as raw address values
    Executable takes input from stdin.
    Takes any nonzero return code as crash to work with QEMU'''

    def __init__(self,
                 args:list[str],
                 env:dict,
                 ostream,
                 timeout_sec=1,
                 address_size=8,
                 address_byte_order='little'):
        self.args = args
        self.env = env
        self.ostream = ostream
        assert ostream in ('stdout', 'stderr')
        self.address_size = address_size
        self.address_byte_order = address_byte_order
        assert address_byte_order in ('little', 'big')
        self.timeout_sec = timeout_sec

    def copy(self):
        return RawTraceOutputTarget(self.args, self.env, self.ostream)

    def run(self, inp):
        if self.ostream == 'stdout':
            o, e = subprocess.PIPE, subprocess.DEVNULL
        else:
            o, e = subprocess.PIPE, subprocess.DEVNULL

        try:
            p = subprocess.run(self.args,
                            input=inp,
                            stdout=o,
                            stderr=e,
                            env=self.env,
                            timeout=self.timeout_sec)
        except TimeoutError:
            return False, set()
        else:
            return p.returncode == 0, self._get_trace(p.stdout if self.ostream == 'stdout' else p.stderr)

    def _get_trace(self, ostream:bytes):
        return set(int.from_bytes(bytes(i), self.address_byte_order, signed=False)
                for i in mit.chunked(ostream, self.address_size))

