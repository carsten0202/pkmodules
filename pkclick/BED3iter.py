###########################################################
#
# ---%%%  Class BED3iter: Iterate over BED data  %%%---
#

import logging

logger = logging.getLogger(__name__)

# NOTE: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  CLASS: BED3iter  %-

class BED3iter(object):
    """Class to iterate over BED data. Will return BED3 only which is the first three columns of a BED file. Will set col3 to col2 if missing."""
    def __init__(self, iterator):
        """
        iterator: Iterator which returns rows of BED data as lists (or tuples).
        """
        self.iter = iterator
        logger.debug(f"BED3iter: I'm here!")

    def __iter__(self):
        return self
    
    def __next__(self):
        row = next(self.iter)
        try:
            (chrom, start, stop, *_) = row
        except ValueError:
            try:
                (chrom, start) = row
                stop = start
            except Exception as e:
                logger.error(f" Encountered {e}")
        return (chrom, start, stop)

    def __add__(self, other):
        from itertools import chain
        try:
            logger.debug(f" Joining {iter(other)} and {self}")
            return chain(self, iter(other))
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        from itertools import chain
        try:
            logger.debug(f" Joining {iter(other)} and {self}")
            return chain(iter(other), self)
        except TypeError:
            return NotImplemented

