###########################################################
#
# ---%%%  Class BED3: Handling BED data in Click  %%%---
#

import click
import logging

from .BED3iter import BED3iter

logger = logging.getLogger(__name__)

# NOTE: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  CLASS: pkclick.BED3  %-

class BED3(click.File):
    """A class for opening files with data columns and returning them as a list without headline.
       Output: An iterator which returns each line in a bed file as a list of the column values."""
    name = "BED_FILE"

    def convert(self, value, param, ctx):
        """Convert by calling csv.reader on filehandle."""
        import pklib.pkcsv as csv
        if not isinstance(value, type(str())):
            return value
        try:
            f = super().convert(value, param, ctx)
            logger.debug(f" Reading data table from '{f.name}'")
            return BED3iter(csv.reader(f, comment_char="#"))
        except Exception as e:
            logger.error(f" {e}")
            self.fail(f"ERROR: Unable to open '{value}' as a BED file.")
