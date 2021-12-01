
#
# --%% plclick.py  %%--
#
 
__version__ = "1.1.2"

import click
import codecs
import logging

logger = logging.getLogger(__name__)


# TODO: Here's some fun. All click type extenders must obey these five guys:
#    it needs a name
#    it needs to pass through None unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being None. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  Class pkclick.gzFile  %-

def unicodeerror_handler(exc): 
	logger.warning(f"Current codec '{exc.encoding}' can't decode byte {exc.object[exc.start:exc.end]} found in input. Byte will be replaced with '?'.")
	logger.info(exc.object[0:exc.start] + "?" + exc.object[exc.end:])
#	return (f"{exc.object[0:exc.start]}?{exc.object[exc.end:]}", exc.end)
	return (u"[bad char]", exc.end)
codecs.register_error("UnicodeError", unicodeerror_handler)


class gzFile(click.File):
	"""A Class for detecting compressed files and automagically decrompress them."""
	magic_dict = {
		b"\x1f\x8b\x08"     : "gz",
		b"\x42\x5a\x68"     : "bz2",
		b"\x50\x4b\x03\x04" : "zip"
	}

	def convert(self, value, param, ctx):
		"""Converts (extracts) compressed input."""
		import gzip
		import io
		f = super().convert(value, param, ctx)
		if hasattr(f, 'name'):
			logger.info(f"Reading from '{f.name}'")
		try:
			if self._getziptype(f, self.magic_dict) is not None:
				return io.TextIOWrapper(gzip.GzipFile(fileobj=f), errors='replace')
		except UnicodeDecodeError:
			self.fail("Could not interpret input. Did you remember to use binary mode? eg gzFile(mode='rb')")
		return io.TextIOWrapper(f, errors='UnicodeError')

	@staticmethod
	def _getziptype(f, magic_dict):
		"""If f is seekable, return the zip flavor."""
		logger.debug(f"gzFile: Input is seekable = {f.seekable()}.")
		if f.seekable():
			file_sample = f.read(max(len(x) for x in magic_dict))
			logger.debug(f"gzFile: Sniffer sample = '{file_sample}'.")
			f.seek(0)
			for magic, filetype in magic_dict.items():
				if file_sample.startswith(magic):
					logger.info(f"gzFile: File type determined = {filetype}.")
					return filetype
		return None



#
# -%  CLASS: pkclick.csv  %-

class CSV(click.ParamType):
	"""A Class for handling option values that are comma separated values."""
	name = "csv_list"
	def convert(self, value, param, ctx):
		import csv
		value = super().convert(value, param, ctx)
		out = next(csv.reader([value]))
		logger.debug(f"CSV Convert: Read list = {out}.")
		return out



#
# -%  CLASS: SampleList  %-

class SampleList(gzFile):
	"""Obtain a list of samples from a file (or '-'... maybe?)."""
	def convert(self, value, param, ctx):
		f = super().convert(value, param, ctx)
		logger.debug(f"SampleList: Input is seekable = {f.seekable()}.")
		if self._isVCF(f):
			logger.info("SampleList: Treating samples file as VCF.")
			try:
				import vcf
				vcf_r = vcf.Reader(f, compressed=False)
				record = next(vcf_r)
				samples = [subject.sample for subject in record.samples]
			except ImportError:
				self.fail("Encountered VCF imput but could not find the PyVCF module. Either install with 'pip install PyVCF' or provide different input.")
		elif self._isTable(f):
			import pklib.pkcsv as csv
			riter = csv.reader(f)
			hdr = next(riter)[0]
			logger.debug(f"SampleList: Treating samples file as Table/CSV. Reading from column '{hdr}'.")
			samples = [hdr] + [row[0] for row in riter]
		else:
			logger.info("SampleList: Treating samples file as list of plain IDs.")
			samples = [line.rstrip() for line in f.readlines()]
		logger.debug(f"SampleList: samples[:10]={samples[:10]}.")
		logger.info(f"SampleList: Read {len(samples)} sample identifiers.")
		return samples
#		self.fail("Could not parse input. Please try a different file format.")

	@staticmethod
	def _isVCF(f):
		"""Is f a VCF file? Returns 'None' if it couldn't check f."""
		if f.seekable():
			file_sample = f.readline()
			logger.debug(f"SampleList: Sniffer sample = '{file_sample}'.")
			f.seek(0)
			return file_sample.startswith("##fileformat=VCFv4")
		return None

	@staticmethod
	def _isTable(f):
		"""Is f a tsv/csv file? Returns 'None' if it couldn't check f."""
		if f.seekable():
			import csv
			file_line = f.readline()
			file_sample = f.read(1024)
			logger.debug(f"SampleList: First line looks like this: '{file_line}'.")
			f.seek(0)
			try: dialect = csv.Sniffer().sniff(file_sample)
			except csv.Error:
				return False
			return len(next(csv.reader([file_line], dialect))) > 1
		return None



#
# -%  CLASS: TimeDelta %-

class Timedelta(click.ParamType):
	"""Class for recording time intervals and the like as pd.Timedelta."""
	name = "time_str"
	def convert(self, value, param, ctx):
		value = super().convert(value, param, ctx)
		try: (n, u) = value.split()
		except AttributeError:
			return value # This will return if value is not a string making function idempotent
		except ValueError:
			(n, u) = ("1", value)
		if u.lower() in ("week", "weeks"):
			(n, u) = (float(n) * 7, "days")
		elif u.lower() in ("month", "months"):
			(n, u) = (float(n) * 30.44, "days")
		elif u.lower() in ("year", "years"):
			(n, u) = (float(n) * 365.2425, "days")
		import pandas as pd
		try: return pd.Timedelta(str(n) + " " + u)
		except ValueError:
			self.fail(f"'{value}' could not be converted to a delta time value.")

#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to call self.fail() if conversion fails


