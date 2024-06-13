
##########################################################
#
# --%%  pkpgs.py - Use the pgscatalogs tools to download and parse pgs risk score files  %%--
#

import click
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# NOTE: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

class PGSFile(click.File):
	"""A class for parsing a PGS file using pgscatalog."""
	name = "PGSFILE"

	def convert(self, value, param, ctx):
		from pgscatalog.core import ScoringFile
		if value is None or isinstance(value, ScoringFile):
			return value
		pgs = ScoringFile(value)
		if not Path(value).exists():
			try:
				pgs.download(".") # TODO: Where should we put score files?
			except FileExistsError:
				if not Path(value).exists():
					pgs = ScoringFile(f"{value}.txt.gz")
				logger.debug(f"convert: '{pgs.local_path}' exists - Download aborted")
			except:
				self.fail(f"ERROR: Unable to open '{value}' as a risk score")
		return pgs



#
# -%  The Cabinet of Horrors  %-
# Subclassing the pgsutils to include the complex columns in ScoreVariant

# from unittest.mock import patch
# @patch('pgscatalog.core.lib._read.ScoreVariant')
# def read_rows_lazy(
# 	*, csv_reader, fields: list[str], name: str, wide: bool, row_nr: int
# ):
# 	import sys
# 	sys.exit("Patched")


# def read_rows_lazy(
#     *, csv_reader, fields: list[str], name: str, wide: bool, row_nr: int
# ):
#     """Read rows from an open scoring file and instantiate them as ScoreVariants"""
#     for row in csv_reader:
#         variant = dict(zip(fields, row))

#         if wide:
#             ew_col_idxs: list[int] = [
#                 i for i, x in enumerate(["effect_weight_" in x for x in fields]) if x
#             ]
#             for i, weight_name in zip(ew_col_idxs, [fields[i] for i in ew_col_idxs]):
#                 yield ScoreVariant(
#                     **variant,
#                     **{
#                         "accession": weight_name,
#                         "row_nr": row_nr,
#                         "effect_weight": variant[weight_name],
#                     },
#                 )
#         else:
#             yield ScoreVariant(**variant, **{"accession": name, "row_nr": row_nr})

#         row_nr += 1

