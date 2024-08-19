###########################################################
#
# ---%%%  Class VCFFile: Handling VCF data in Click  %%%---
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
# -%  CLASS: pkclick.VCFFile  %-

class VCFFile(click.File):
	"""A class for parsing a VCF file using pysam."""
	name = "VCF_FILE"
	def convert(self, value, param, ctx):
		"""Convert by reading VCF with pysam VariantFile."""
		if isinstance(value, str):
			logger.debug(f"This is my value: {value}")
			try:
				from pysam import BGZFile, VariantFile
				if 'r' in self.mode:
					logging.debug(f"VCFFile: Reading variant info from {value}")
					return VariantFile(value)
				elif 'w' in self.mode and value.endswith(".gz"):
					logging.debug(f"VCFFile: Writing variant info to BGZfile {value}")
					return BGZFile(value, self.mode)
				else:
					return open(value, mode = self.mode)
			except ImportError as e:
				logging.debug(e)
				self.fail("ERROR: Encountered VCF imput but could not import the PySAM module for reading VCF input.i\nERROR: Please make sure PySAM isinstalled or use alternative input.")
			except Exception as e:
				logging.debug(e)
				self.fail(f"ERROR: Unable to open '{value}' as a VCF file.")
		return value

