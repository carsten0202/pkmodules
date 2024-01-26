
###########################################################
#
# --%%  pkpysam.py - Home for oClick options which read in datafiles using pysam classes  %%--
#

# TODO: It's time to split up the pkclick file...

# NOTE: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  CLASS: pkclick. ...something with tabix?...  -%

#class VCFFile(click.File):
#	"""A class for parsing a VCF file using pysam."""
#	name = "VCFFILE"

