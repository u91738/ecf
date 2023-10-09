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


def tokenize(inp):
    '''Generic text tokenization by words of alnum, space, punctuation and "other"'''
    special = b'!@#$%^&*()\'"[]{}:;\\/.,<>-=_+\0'
    space, alnum, sym, other = 0, 1, 2, 3
    tok_type, tok = None, bytearray()
    res = []
    for i in inp:
        c = chr(i)
        if c.isspace():
            if tok_type is None:
                tok_type = space
            if tok_type == space:
                tok.append(i)
            else:
                res.append(bytes(tok[:1])) # squash multiple spaces
                tok_type, tok = space, bytearray([i])
        elif c.isalnum():
            if tok_type is None:
                tok_type = alnum
            if tok_type == alnum:
                tok.append(i)
            else:
                res.append(bytes(tok))
                tok_type, tok = alnum, bytearray([i])
        elif i in special:
            res.append(bytes([i])) # each symbol is it's own word
            tok_type, tok = sym, bytearray([i])
        else:
            if tok_type is None:
                tok_type = other
            if tok_type == other:
                tok.append(i)
            else:
                res.append(bytes(tok))
                tok_type, tok = other, bytearray([i])

    res.append(bytes(tok[:1] if tok_type == space else tok))
    return tuple(res)
