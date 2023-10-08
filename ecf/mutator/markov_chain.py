import numpy as np

class _MarkovChainImpl:
    '''Internal implementation of byte-by-byte Markov chain'''

    def __init__(self, samples, impossible_transition_prob=None):
        # use 256 for "end of sequence" and 257 as initial state
        m = np.zeros((258,257))
        for sample_group, weight in samples:
            for sample in sample_group:
                if len(sample) == 1:
                    m[257, 256] += weight
                elif len(sample) == 2:
                    m[257, sample[0]] += weight
                    m[sample[0], 256] += weight
                else:
                    a = np.frombuffer(sample, dtype=np.uint8)
                    b = a[1:]
                    m[a[:-1], b] += weight
                    m[b[-1], 256] += weight
                    m[257, a[0]] += weight

        if impossible_transition_prob:
            # give a chance to 'impossible' transitions to make fuzzing fuzzier
            rowlen = m.shape[1]
            good_trans_p = 1 - impossible_transition_prob
            for mi in m:
                total = np.sum(mi)
                if total == 0:
                    mi[:] = 1 / rowlen
                else:
                    zeros = np.isclose(mi, 0)
                    mi[~zeros] *= good_trans_p
                    mi[zeros] = impossible_transition_prob * total / rowlen

            rowsum = np.sum(m, 1)
            m /= np.reshape(rowsum, (-1,1))
            assert np.alltrue(np.isclose(np.sum(m, 1), 1)), f'sum of probabilities must be 1'
        else:
            rowsum = np.sum(m, 1)
            rowsum_nz = rowsum != 0
            m[rowsum_nz] /= np.reshape(rowsum[rowsum_nz], (-1,1))

            res_rowsum = np.sum(m, 1)
            assert np.alltrue(np.isclose(res_rowsum, 1) | np.isclose(res_rowsum, 0)), f'sum of probabilities must be 1'



        self.transitions = m

    def generate(self):
        state = 257
        r = bytearray()
        while True:
            state = np.argmax(self.transitions[state] * np.random.random(257))
            if state == 256:
                break
            else:
                r.append(state)
        return r

class MarkovChain:
    '''Byte-by-byte markov chain generator.
    Learns from samples of this step or whole corpus + weighted samples.
    If impossible_transition_prob is not None,
    each step has a chance to step into a state that is not possible according to known dataset'''

    def __init__(self, corpus=None, impossible_transition_prob=None, samples_weight=3):
        self.corpus = corpus
        self.samples_weight = samples_weight
        self.impossible_transition_prob = impossible_transition_prob
        self.name = type(self).__name__

    def mutate(self, samples, n):
        if self.corpus:
            mc_samples = ((self.corpus.inputs, 1), (samples, self.samples_weight))
            c = _MarkovChainImpl(mc_samples, self.impossible_transition_prob)
        else:
            c = _MarkovChainImpl([(samples, 1)], self.impossible_transition_prob)
        res = [c.generate() for _ in range(n)]
        return res
