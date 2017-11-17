#!/usr/bin/env python3.6

# Should I be more specific that 'blocks' is 'blocksread', and 'remain' is
# 'linesremain'?

# Could get average line length, and then set bufsz default to be
# bufsz_default = 8 (bytes == 1 char) * average_line_len * nlines_default

# It appears I may be making a final empty iteration. But my test passed that
# checked that StopIteration was raised when expected.


__date__ = '2017-11-14'
__version__ = (0,0,1)

"""
Walk backwards through a file yielding successive "chunks" of *nlines*.

Create a new Tail instance, which is an iterable object. Each iteration yields?
the number of lines, in succession, given as the *nlines* argument, of a file
as *fpath*. Thus, *nlines* = 20 yields the last 20 lines of the file, then the
next to last 20, and so on. Use the next function to call its next method to
only tail the file a single time.

If the number of lines requested at any point (initially or during iterations)
the remaining lines are returned. Likewise, if the buffer size (*bufsz*) is
too big for the size of the file, all of the lines will still be returned in
"chunks" of *nlines*.

The lines are returned as a string. This is because the file is read in binary,
and the object is working with bytes, and it is "expensive" to convert each
"binary string" to character strings, and more efficient to join the binary
strings and convert the lot, at once, to character strings. To get a list,
just call the str.splitlines method.

Also included are the `tail` and `tfilter` convenience functions.

`tail` will instantiate a Tail object and iterate over it, producing *nlines*
upon each iteration. By default, its only arguments are *fpath* and *nlines*,
and the guesswork for the buffer size (*bufsz*) is handled for you.  But the
remaining arguments to the Tail object are allowed as keyword arguments.

The `tfilter` function has the same arguments as `tail`, with the addition of
a *func* argument, which must be a callable, with a single string argument.
It creates a Tail instance and iterates over it, applying *func* to each
resulting "chunk" of string (note: each string represents multiple lines from
the file at *fpath*).
"""

from os import SEEK_END, SEEK_CUR
from os.path import exists


class Tail:

    def __init__(self, fpath, nlines=20, bufsz=1024, encoding='utf-8'):
        assert exists(fpath)
        assert int(nlines)
        assert int(bufsz)
        assert str(encoding)
        self.fpath = fpath
        self.encoding = encoding
        self.bufsz = bufsz      # how many bytes to read at a time
        self.blocks = 0         # number of buffers we've read
        self.nlines = nlines    # how many lines to return for each iteration.
        self.posn = None        # "offset"? current byte position in the file.
        self.lines = []         # list of binary strings we have read so far
        self.remain = 0


    def __repr__(self):
        return '{}({})'.format(Tail.__name__,
                    ', '.join((f'{k}={v}' for k,v in self.__dict__.items())))

    def __str__(self):
        # Call next? Not so sure about this, just experimenting.
        # So it shouldn't be affected, it's another instance.
        # It will always print the same lines, right? Probably not what we want.

        # Some attrs aren't arguments, so they've got to be deleted, or
        # only those given passed.
        return next(Tail(**self.__dict__))


    @property
    def totallines(self):
        return len(self.lines)


    def __iter__(self):
        return self


    def __next__(self):
        with open(self.fpath, mode='rb') as f:
            # We've read the whole file. Do any lines remain?
            if self.posn == 0:
                if self.remain:
                    self.blocks += 1
                    nxt_chunk_idx = -1 * (self.nlines * self.blocks)
                    prv_chunk_idx = -1 * (self.nlines * (self.blocks - 1))
                    chunk = self.lines[nxt_chunk_idx:prv_chunk_idx]
                    self.remain = self.totallines - (self.blocks * len(chunk))
                    # We've gone too far. Return the rest. Raise StopIter next.
                    if abs(nxt_chunk_idx) > self.totallines:
                        nxt_chunk_idx = 0 # last line (the first in the file)
                        chunk = self.lines[nxt_chunk_idx:prv_chunk_idx]
                        self.remain = 0
                    return b''.join(chunk).decode(self.encoding) # str
                else:
                    raise StopIteration('the whole file has been consumed.')


            try:
                if not self.posn: # Once we know our posn, we can use it.
                    f.seek(-self.bufsz, SEEK_END) # relative posn
                else:
                    self.posn -= self.bufsz
                    f.seek(self.posn) # 0, whatever os.SEEK for beginning
                self.posn = f.tell() # Now we know our absolute posn.
            except OSError:     # Invalid argument: bufsz > bytes remaining.
                self.posn = 0   # Start of the file. We've consumed it all.
                f.seek(self.posn)


            self.lines = f.readlines()
            self.blocks += 1

            if self.totallines >= self.nlines:
                if self.blocks == 1:
                    chunk = self.lines[-1 * self.nlines:]
                elif self.blocks >= 2: #else:
                    nxt_chunk_idx = -1 * (self.nlines * self.blocks)
                    prv_chunk_idx = -1 * (self.nlines * (self.blocks - 1))
                    chunk = self.lines[nxt_chunk_idx:prv_chunk_idx] # prev_chunks+1?
            else:
                chunk = self.lines # When nlines > totallines in file.
            self.remain = self.totallines - (self.blocks * len(chunk))
            return b''.join(chunk).decode(self.encoding) # str


def tail(fpath, nlines=20, **kwargs):
    """Iterate over a Tail instance yielding the results.
    A convenience function."""
    for chunk in Tail(fpath, nlines, **kwargs):
        yield chunk


def tfilter(fpath, nlines, func, **kwargs):
    # Should I pass a list? string? split the lines and pass each line?
    for chunk in Tail(fpath, nlines, **kwargs):
        yield func(chunk)


if __name__ == '__main__':

    log = '/home/na/git/prisonersDilemma/orionscripts/whois/tests/samples-micro/splunk-export.csv'

    mytail = Tail(log,nlines=20,bufsz=1024)
    for chunk in mytail:
        lines = chunk.splitlines()
        print('-'*60)
        print(f'Current chunk (len: {len(lines)}).')
        print(lines)
        print('-'*60)