
#
# --%%  pkcsv.py    %%--
#

__version__ = "1.4"
# v1.2 : Changed reader into a real classed object.
# v1.3 : Added a try statement to catch errors in DictReader if f isn't correct format.
# v1.4: Added the sniff function
import csv
import itertools
import logging

logger = logging.getLogger(__name__)

class reader(object):
    """Extend 'reader' from csv to add extra functionality."""
    def __init__(self, f, dialect=None, comment_char=None, *args, **kwargs):
        """Autodetects input with sniffer and returns tuple with iter and header."""
        logger.debug(f"csv.reader reading from: {f}")
        if dialect is None:
            (f, dialect) = _configure(f, comment_char=comment_char, dialect=dialect)
        self._reader = csv.reader(f, dialect=dialect, *args, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._reader)

    @property
    def QUOTE_ALL(self):
        return True

class DictReader(csv.DictReader):
    """Extend DictReader from csv to add extra functionality."""
    def __init__(self, f, fieldnames=None, dialect=None, comment_char=None, *args, **kwargs):
        """Autodetects input with sniffer and returns dict with header as keys. Lines starting with comment_char will be skipped."""
        try: logger.debug(f"DictReader: Reading file {f.name}")
        except AttributeError:
            logger.error(f"DictReader: Input doesn't look like a file object. Input={f}; type={type(f)}.")
            exit(1)
        (fout, dialect) = _configure(f, comment_char=comment_char, dialect=dialect)
        header = next(csv.reader([next(fout)], dialect=dialect)) # Extracts header and discards it from fout)
        logger.debug(f"DictReader reading columns: {header}")
        super().__init__(fout, fieldnames=header, dialect=dialect, *args, **kwargs)

def _configure(f, dialect=None, comment_char=None, delimiters=None):
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
    dialect = csv.Sniffer().sniff(line1 + line2, delimiters) if dialect is None else dialect
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

