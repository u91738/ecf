# ECF
A coverage guided fuzzing framework adaptable for unusual targets.

The goal of this project is to provide a Python framework to fuzz anything that can provide *some* form of coverage info.
Anything that can give a set of numbers will do.

Some software needs to run in unusual environments, be it VM with customized DOS or locked down embedded platform, you may be unable to run conventional tools.
With ECF, you need to write a target class that can get the coverage data off the target.
For example if you can get gcov-instrumented binary running on the target, you would extend GCovTarget like
```
# define custom target
class SomeTarget(GCovTarget):
    def run(self, input):
        # somehow apply input to your target
        # get *.gcda to directory in self.playground.name
        success = True # True if did'nt crash
        return success, self._last_trace()

# create target
t = SomeTarget(['path', 'and', 'args', 'used', 'in', 'run()'], ['/path/to/some.gcno'])
initial_corpus = read_corpus_dir('./corpus')
mutator = BitFlip(1, 4)
fuzz = Fuzz(SequentialTargetRunner(t), mutator, initial_corpus, 1000)
while True:
    crashes = fuzz.step()
    for c in crashes:
        print('crash found with input: ', hexlify(c))
        break
```

For more usage examples (multiple mutators, parallel execution) see `example-*.py`.
If you want to play with examples, update git submodules, then `cd example-data && make`.
