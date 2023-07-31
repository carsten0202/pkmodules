##################################################
#
# --%%  : 'Locus' Class Definition  %%--

import logging
import re

logger = logging.getLogger(__name__)

class Locus(object):
    """A base class to hold one genomic position"""
    def __init__(self, chrom=None, pos=None, ID=None, build=None):
        assert any([ID is not None, chrom and pos]), "A Locus must have an ID or a Chromosome Position (Chrom + pos)."
        if all([chrom is None, pos is None]):
            if re.search("^[0-9xXyYmM]+:[0-9]+", ID):
                (chrom,pos,*_) = ID.split(":")
        self.chrom = str(chrom) if chrom else None
        self.pos   = int(pos) if pos else None
        self.ID    = str(ID) if ID is not None else self.posid
        self.build = build

    def __eq__(self, other):
        """A match is True if Chr+Pos and ID matches One pair can be missing; either chr+pos or ID, but not both."""
        if isinstance(other, Locus):
            same = [self.ID == other.ID]
            same.extend([self.chrom == other.chrom and self.pos == other.pos] if None not in [self.chrom, other.chrom, self.pos, other.pos] else [])
            return any(same)
        return NotImplemented

    @property
    def posid(self):
        """Return the position id."""
        if all([self.chrom, self.pos]):
            return f"{self.chrom}:{self.pos}"
        return None

# --%%  : 'Locus' Class Definition  %%--
#
##################################################


