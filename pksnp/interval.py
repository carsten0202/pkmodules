
__version__ = "1.0"


import itertools
import logging

from .locus import Locus

logger = logging.getLogger(__name__)


##################################################
#
# --%%  : 'Ingerval' Class Definition  %%--

class Interval(Locus):
    """A base class to hold a genomic interval."""
    def __init__(self, chrom=None, pos=None, end=None, ID=None, build=None, start=None):
        """Start position is mandatory, but end is optional."""
        assert pos == start or None in [pos, start], "Please do not specify different values for 'pos' and 'start'"
        self.end = int(end) if end else None
        super().__init__(chrom, pos=start if pos is None else pos, ID=ID, build=build)

    @classmethod
    def fromStr(cls, string):
        """Alternative constructor for when you have a text string like 'CHROM pos end ID reference'."""
        assert isinstance(string, str), "fromStr expects precicely one argument which should be a string."
        return cls(*string.split())

    def __eq__(self, other):
        """A match is True if Chr+Pos and ID matches One pair can be missing; either chr+pos or ID, but not both."""
        if isinstance(other, Locus):
            same = [self.ID == other.ID]
            same.extend([self.chrom == other.chrom and self.pos == other.pos] if None not in [self.chrom, other.chrom, self.pos, other.pos] else [])
            return any(same)
        return NotImplemented

    def __repr__(self):
        return self.__str__() + "\n"

    def __str__(self):
         return "\t".join(self.region)

    @property
    def posid(self):
        """Return the position id."""
        if all([self.chrom, self.start, self.end]):
            return f"{self.chrom}:{self.start}:{self.end}"
        elif all([self.chrom, self.start]):
            return f"{self.chrom}:{self.start}"
        return None

    @property
    def region(self):
        """An array with the region, bcftools style. Hey, here's a crazy idea: Keep this as the primary, and let chrom, pos, and the others be properties???"""
        return super().region if self.end is None else super().region + [str(self.end)]

    @property
    def start(self):
        """Return pos using start alias."""
        return self.pos

# --%%  : 'Interval' Class Definition  %%--
#
##################################################



##################################################
#
# --%%  : 'IntervalList' Class Definition  %%--

class IntervalList():
    """An iterable which functions like a list of intervals."""
    def __init__(self, iterable):
        """Takes an iterable which should return something that can be processed with """
        self._intervals = iter([])
        for locus in iterable:
            self.append(locus)

    def __iter__(self):
        """"""
        return self

    def __next__(self):
        """"""
        return next(self._intervals)

    def append(self, interval):
        """Try to convert interval into Interval and append it to the stack."""
        if not isinstance(interval, Interval):
            if isinstance(interval, str):
                interval = Interval.fromStr(interval)
            elif isinstance(interval, dict) or isinstance(interval, list):
                interval = Interval(*interval)
            else:
                assert False, "Failed to convert."
        self._intervals = itertools.chain(self._intervals, [interval])

# --%%  : 'IntervalList' Class Definition  %%--
#
##################################################


