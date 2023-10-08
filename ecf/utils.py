import os

def read_corpus_dir(path):
    '''Read contents of each file in a directory into a list'''
    r = []
    for i in os.listdir(path):
        p = os.path.join(path, i)
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                r.append(f.read())
    return r
