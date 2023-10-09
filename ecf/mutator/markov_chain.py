import numpy as np
from ecf.utils import tokenize

def set_zero_probs(m, impossible_transition_prob):
    '''For a transition matrix, in-place
    set zero cells so that their sum makes total of impossible_transition_prob for each row'''
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
    return m


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
            set_zero_probs(m, impossible_transition_prob)
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


class _MarkovChainDictImpl:
    '''Internal implementation of arbitrary int state set Markov chain'''

    def __init__(self, samples, state_count, impossible_transition_prob=None):
        self.state_count = state_count
        m = np.zeros((state_count + 2, state_count + 1))
        for sample_group, weight in samples:
            for sample in sample_group:
                if len(sample) == 1:
                    m[-2, -1] += weight
                elif len(sample) == 2:
                    m[-1, sample[0]] += weight
                    m[sample[0], -1] += weight
                else:
                    a = np.array(sample, dtype=np.uint32)
                    b = a[1:]
                    m[a[:-1], b] += weight
                    m[b[-1], -1] += weight
                    m[-1, a[0]] += weight

        if impossible_transition_prob:
            # give a chance to 'impossible' transitions to make fuzzing fuzzier
            set_zero_probs(m, impossible_transition_prob)
        else:
            rowsum = np.sum(m, 1)
            rowsum_nz = rowsum != 0
            m[rowsum_nz] /= np.reshape(rowsum[rowsum_nz], (-1,1))

            res_rowsum = np.sum(m, 1)
            assert np.alltrue(np.isclose(res_rowsum, 1) | np.isclose(res_rowsum, 0)), f'sum of probabilities must be 1'

        self.transitions = m

    def generate(self):
        state = self.state_count + 1
        r = []
        while True:
            state = np.argmax(self.transitions[state] * np.random.random(self.state_count + 1))
            if state == self.state_count:
                break
            else:
                r.append(state)
        return r


class MarkovChainDict:
    '''Dictionary-based markov chain. Generates sequence of words seen in samples or corpus'''

    def __init__(self, corpus=None, impossible_transition_prob=None, samples_weight=3):
        self.corpus = corpus
        self.samples_weight = samples_weight
        self.impossible_transition_prob = impossible_transition_prob
        self.name = type(self).__name__

    def tokenize(self, inp):
        return tokenize(inp)

    def __tokenize_all(self, inputs):
        return [self.tokenize(i) for i in inputs]

    def __states_to_input(self, dictionary, states):
        return b''.join(dictionary[state] for state in states)

    def __tokens_to_states(self, dictionary, tokens):
        return [dictionary[token] for token in tokens]

    def mutate(self, samples, n):
        corpus_tokens = self.__tokenize_all(self.corpus.inputs) if self.corpus else []
        sample_tokens = self.__tokenize_all(samples)
        dictionary = list(set(token for sample_group in (corpus_tokens, sample_tokens)
                                    for sample in sample_group
                                    for token in sample))
        rev_dictionary = {token: i for i, token in enumerate(dictionary)}
        mc_samples = (
            ([self.__tokens_to_states(rev_dictionary, i) for i in corpus_tokens], 1),
            ([self.__tokens_to_states(rev_dictionary, i) for i in sample_tokens], self.samples_weight))
        c = _MarkovChainDictImpl(mc_samples, len(dictionary), self.impossible_transition_prob)
        return [self.__states_to_input(dictionary, c.generate()) for _ in range(n)]
