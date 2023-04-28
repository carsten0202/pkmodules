
#
# --%%  pkcsv.py  %%--
#

__version__ = "1.1"

import csv
import itertools
import logging

logger = logging.getLogger(__name__)

def reader(f, dialect=None, **fmtparams):
	"""Autodetects input with sniffer and returns tuple with iter and header."""
	try: logger.debug(f"Reading from: {f.name}")
	except:	pass
	if dialect is None:
		(fout, dialect) = _configure(f, dialect=dialect)
		riter = csv.reader(fout, dialect=dialect, **fmtparams)
	else:
		riter = csv.reader(f, dialect=dialect, **fmtparams)
	return riter

class DictReader(csv.DictReader):
	"""Extend DictReader from csv to add extra functionality."""
	def __init__(self, f, fieldnames=None, dialect=None, comment_char=None, *args, **kwargs):
		"""Autodetects input with sniffer and returns dict with header as keys. Lines starting with comment_char will be skipped."""
		logger.debug(f"DictReader file: {f}")
		(fout, dialect) = _configure(f, comment_char=comment_char, dialect=dialect)
		header = next(csv.reader([next(fout)], dialect=dialect)) # Extracts header and discards it from fout)
		logger.debug(f"DictReader columns: {header}")
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
	logger.debug(f"Sniffer evaluating: {line1 + line2}")
	dialect = csv.Sniffer().sniff(line1 + line2, delimiters) if dialect is None else dialect
	reader = csv.reader([line1, line2], dialect)
	header = next(reader)
	second = next(reader)
	logger.debug(f"Reading Columns: {header} {second}")
	if len(header) + 1 == len(second):
		logger.info(f"R table format detected in input.")
		header = ["row.index"] + header
	return f2, dialect

