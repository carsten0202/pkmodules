
#
# --%%  pkcsv.py    %%--
#

__version__ = "1.4.0"
# 1.2 : Changed reader into a real classed object.
# 1.3 : Added a try statement to catch errors in DictReader if f isn't correct format.
# 1.4 : Made _configure and the sniffer part more robust with try, except clause

import csv
import itertools
import logging

logger = logging.getLogger(__name__)

class reader(object):
    """Extend 'reader' from csv to add extra functionality."""
    def __init__(self, f, dialect=None, comment_char=None, delimiter=None, *args, **kwargs):
        """Autodetects input with sniffer and returns tuple with iter and header."""
        logger.debug(f"csv.reader reading from: {f}")
        (fout, dialect) = _configure(f, comment_char=comment_char, dialect=dialect, delimiter=delimiter)
        self._reader = csv.reader(fout, dialect=dialect, *args, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._reader)

    @property
    def QUOTE_ALL(self):
        return True

class DictReader(csv.DictReader):
    """Extend DictReader from csv to add extra functionality."""
    def __init__(self, f, fieldnames=None, dialect=None, comment_char=None, delimiter=None, *args, **kwargs):
        """Autodetects input with sniffer and returns dict with header as keys. Lines starting with comment_char will be skipped."""
        logger.debug(f"csv.DictReader reading from: {f}")
        (fout, dialect) = _configure(f, comment_char=comment_char, dialect=dialect, delimiter=delimiter)
        header = next(csv.reader([next(fout)], dialect=dialect)) # Extracts header and discards it from fout)
        logger.debug(f"DictReader reading columns: {header}")
        super().__init__(fout, fieldnames=header, dialect=dialect, *args, **kwargs)

def _configure(f, dialect=None, comment_char=None, delimiter=None):
    """Check input and find header and readable iterator."""
    (f1, f2) = itertools.tee(f,2)
    if comment_char:
        while ((line1 := next(f1)).startswith(comment_char)):
            next(f2) # Discards all lines starting with comment_char from beginning of file.
        while ((line2 := next(f1)).startswith(comment_char)):
            pass
    else:
        line1 = next(f1)
        line2 = next(f1)
    logger.debug(f"Sniffer evaluating line1: {line1.rstrip()}")
    logger.debug(f"Sniffer evaluating line2: {line2.rstrip()}")
    if dialect is None:
        logger.debug(f"PKCSV: Dialect = {dialect}; Delimiter = {delimiter}")
        try: dialect = csv.Sniffer().sniff(line1 + line2, delimiter)
        except csv.Error:
            logger.error(f"PKCSV: _configure unable to determine delimiter. Input treated as single column (Not yet implemented).")
            exit("Exited due to unimplemented feature.")
        logger.debug(f"PKCSV: Dialect = {dialect}; Delimiter = {delimiter}")
    reader = csv.reader([line1, line2], dialect)
    header = next(reader)
    second = next(reader)
    logger.debug(f"Parsing input header: {header}")
    logger.debug(f"Parsing input first row: {second}")
    if len(header) + 1 == len(second):
        logger.info(f"R table format detected in input.")
        header = ["row.index"] + header
    return f2, dialect

def sniff(f, comment_char=None, delimiters=None):
    if not f.seekable():
        logger.warning(f"Format_sniffer: Reading from '{f.name}' which isn't searchable. Reading will be slow.")
        return None
    line1, line2 = _get_two_lines(f, comment_char)
    f.seek(0)
    dialect = csv.Sniffer().sniff(line1 + line2, delimiters)
    return dialect

def _get_two_lines(f, comment_char=None):
    if comment_char:
        while ((line1 := next(f)).startswith(comment_char)):
            pass
        while ((line2 := next(f)).startswith(comment_char)):
            pass
    else:
        line1 = next(f)
        line2 = next(f)
    return (line1, line2)

