from typing import Union
from angr.project import Project
from angr.sim_state import SimState
from angr.exploration_techniques import LengthLimiter, MemoryWatcher, Timeout

class AngrTarget:
    '''Use angr as an execution environment.
    Fuzzing with angr is slow and only useful
    if in all other cases angr gets state explosion'''
    def __init__(self, project:Project, length_limit=None, timeout=None):
        assert isinstance(project, Project)
        self.project = project
        self.length_limit = length_limit
        self.timeout = timeout

    def copy(self):
        return self # no reasonably mutable state

    def get_state(self, inp:Union[bytes, bytearray]) -> SimState:
        raise NotImplementedError

    def _state_trace(self, *stashes):
        cfg = self.project.kb.cfgs.get_most_accurate()
        assert (cfg is not None) and (len(cfg.nodes()) > 0), 'project must have a CFG'
        res = set()
        for stash in stashes:
            for state in stash:
                for step in state.history.lineage:
                    res.add(step.addr)
        return res

    def run(self, inp):
        st = self.get_state(inp)
        sim = self.project.factory.simulation_manager(st, save_unconstrained=True)
        if self.length_limit:
            sim.use_technique(LengthLimiter(self.length_limit))
        if self.timeout:
            sim.use_technique(Timeout(self.timeout))
        sim.use_technique(MemoryWatcher())
        sim.explore()
        if sim.unconstrained:
            return False, self._state_trace(sim.unconstrained)
        else:
            return True, self._state_trace(*sim.stashes.values())
