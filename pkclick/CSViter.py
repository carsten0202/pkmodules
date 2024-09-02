###########################################################
#
# ---%%%  Class CSViter: Handling CSV data in Click  %%%---
#

import click
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
# -%  CLASS: pkclick.CSVIter  %-

class CSViter(click.File):
    """A class for opening files with data columns and returning them as a list without headline.
       Output: An object which behaves like a csv.reader"""
    def convert(self, value, param, ctx):
        """Convert by calling csv.reader on filehandle."""
        import pklib.pkcsv as csv
        if value is None or isinstance(value, csv.reader):
            return value
        try:
            f = super().convert(value, param, ctx)
            logging.debug(f"CSVIter: Reading data table from '{f.name}'")
            return csv.reader(f, comment_char="#")
        except Exception as e:
            logging.debug(e)
            self.fail(f"ERROR: Unable to open '{value}' as a column-based text file.")

