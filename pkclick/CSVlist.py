###########################################################
#
# ---%%%  Class CSVlist: Handling CSV data in Click  %%%---
#

import logging

from .CSViter import CSViter

logger = logging.getLogger(__name__)

# NOTE: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  CLASS pkclick.CSVList  %-

class CSVlist(CSViter):
    """A class for opening files with data columns and returning them as a list without headline.
       Output: Like CSViter, but returns a list, not an iterator {e.g. like list(csv.reader())}"""
    def convert(self, value, param, ctx):
        """Convert the iterator from parent to a list."""
        if value is None or isinstance(value, list):
            return value
        return list(super().convert(value, param, ctx))

