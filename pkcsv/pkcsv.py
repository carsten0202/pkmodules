
#
# --%%  pkcsv.py  %%--
#

__version__ = "1.0.2"

import csv
import itertools
import logging

logger = logging.getLogger(__name__)

def reader(f, dialect=None, **fmtparams):
	"""Autodetects input with sniffer and returns tuple with iter and header."""
	(header, fout, dialect) = _configure(f, dialect)
	riter = csv.reader(fout, dialect=dialect, **fmtparams)
	return riter

def DictReader(f, fieldnames=None, dialect=None, *args, **kwds):
	"""Autodetects input with sniffer and returns dict with header as keys."""
	(header, fout, dialect) = _configure(f, dialect)
	next(fout)
	riter = csv.DictReader(fout, fieldnames=header, dialect=dialect, *args, **kwds)
	return riter

def _configure(f, dialect=None):
	"""Check input and find header and readable iterator."""
	logger.debug(f"Reading from: {f}")
	(f1, f2) = itertools.tee(f,2)
	line1 = next(f1)
	line2 = next(f1)
	dialect = csv.Sniffer().sniff(line1 + line2) if dialect is None else Dialect
	reader = csv.reader([line1, line2], dialect)
	header = next(reader)
	second = next(reader)
	logger.debug(f"Reading Columns: {header} {second}")
	if len(header) + 1 == len(second):
		logger.info(f"R table format detected in input.")
		header = ["row.index"] + header
	return header, f2, dialect

