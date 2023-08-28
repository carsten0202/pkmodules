
#
# --%% plclick.py  %%--
#
 
__version__ = "1.6"
# 1.4 : Added CSVList to the family
# 1.5 : Made CSVlist indempotent. Should now obey the click law below
# 1.6 : Looks lie I managed to add isal to the list

import click
import codecs
import logging

logger = logging.getLogger(__name__)

# TODO: Here's some fun. All click type extenders must obey these guys:
#    it needs a name
#    it needs to pass through 'None' unchanged
#    it needs to convert from a string
#    it needs to convert its result type through unchanged (eg: needs to be idempotent)
#    it needs to be able to deal with param and context being 'None'. This can be the case when the object is used with prompt inputs.
#    it needs to call self.fail() if conversion fails

#
# -%  Class pkclick.gzFile  %-

def unicodeerror_handler(exc): 
    logger.warning(f"Current codec '{exc.encoding}' can't decode byte {exc.object[exc.start:exc.end]} found in input. Byte will be replaced with '?'.")
    logger.info(f"{exc.object[0:exc.start]}?{exc.object[exc.end:]}")
    return (f"{exc.object[0:exc.start]}?{exc.object[exc.end:]}", exc.end)

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
        try: logger.info(f" Reading from '{f.name}'")
        except AttributeError: logger.info(f"Reading from'{f}'")
        try:
            if self._getziptype(f, self.magic_dict) is not None:
                return io.TextIOWrapper(gzip.GzipFile(fileobj=f), errors='UnicodeError')
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

    @classmethod
    def cast(cls, fobj):
        """Cast most file objects into a fileobject processed by gzFile."""
        import gzip
        import io
        try: logger.info(f"Reading from '{fobj.name}'")
        except AttributeError: logger.info(f"Reading from'{fobj}'")
        try:
            if cls._getziptype(fobj, cls.magic_dict) is not None:
                return io.TextIOWrapper(gzip.GzipFile(fileobj=fobj), errors='UnicodeError')
        except UnicodeDecodeError:
            logger.error("Could not interpret input. Did you remember to use binary mode? eg gzFile(mode='rb')")
            exit(1)
        return io.TextIOWrapper(fobj, errors='UnicodeError')



#
# -%  CLASS: pkclick.isalFile

class isalFile(gzFile):
    """A Class for detecting compressed files and automagically decrompress them. Like gzFile but faster."""

    def convert(self, value, param, ctx):
        """Converts (extracts) compressed input."""
        from isal import igzip
        import io
        f = super(gzFile, self).convert(value, param, ctx)
        try: logger.info(f" Reading from '{f.name}'")
        except AttributeError: logger.info(f"Reading from'{f}'")
        try:
            if self._getziptype(f, self.magic_dict) is not None:
                return io.TextIOWrapper(igzip.IGzipFile(fileobj=f), errors='UnicodeError')
        except UnicodeDecodeError:
            self.fail("Could not interpret input. Did you remember to use binary mode? eg gzFile(mode='rb')")
        return io.TextIOWrapper(f, errors='UnicodeError')




#
# -%  CLASS: pkclick.csv  %-

class CSV(click.ParamType):
    """A Class for handling option values that are comma separated values."""
    name = "csv_list"

    def convert(self, value, param, ctx):
        import csv
        if isinstance(value, list):
            return value
        value = super().convert(value, param, ctx)
        out = next(csv.reader([value]))
        logger.debug(f"CSV Convert: Read list = {out}.")
        return out



#
# -%  CLASS: pkclick.CSVIter  %-

class CSVIter(click.File):
    """A class for opening files with data columns and returning them as a list without headline.
       Output: An obejct which behaves like a csv.reader"""
    def convert(self, value, param, ctx):
        """Convert by calling csv.reader on filehandle."""
        import pklib.pkcsv as csv
        if value is None or isinstance(value, csv.reader):
            return value
        try:
            f = super().convert(value, param, ctx)
            logging.debug(f"CSVList: Reading data table from '{f.name}'")
            return csv.reader(f, comment_char="#")
        except Exception as e:
            logging.debug(e)
            self.fail(f"ERROR: Unable to open '{value}' as a column-based text file.")



#
# -%  CLASS: pkclick.CSVfile  %-

class CSVFile(click.File):
    """A class for opening files and automatically push them through my csv package. File should have a headline used to create the keys for the dict from DictReader.
       Output: An object which behaves like a DictReader."""
    def convert(self, value, param, ctx):
        """Convert by calling DictReader on filehandle."""
        import pklib.pkcsv as csv
        if value is None or isinstance(value, csv.DictReader):
            return value
        try:
            f = super().convert(value, param, ctx)
            logging.debug(f"CSVFile: Reading data table from '{f.name}'")
            return csv.DictReader(f, comment_char="#")
        except Exception as e:
            logging.debug(e)
            self.fail(f"ERROR: Unable to open '{value}' as a column-based text file.")



#
# -%  CLASS pkclick.CSVList  %-

class CSVList(CSVIter):
    """A class for opening files with data columns and returning them as a list without headline.
       Output: Like CSVIter, but returns a list, not an iterator {e.g. like list(csv.reader())}"""
    def convert(self, value, param, ctx):
        """Convert the iterator from parent to a list."""
        if value is None or isinstance(value, list):
            return value
        return list(super().convert(value, param, ctx))



#
# -%  CLASS: pkclick.VCFFile  -%

class VCFFile(click.File):
    """A class for parsing a VCF file using pysam."""
    name = "VCFFILE"

    def convert(self, value, param, ctx):
        """Convert by reading VCF with pysam VariantFile."""
        try: from pysam import VariantFile
        except ImportError as e:
            logging.debug(e)
            self.fail("ERROR: Encountered VCF imput but could not import the PySAM module for reading VCF input.i\nERROR: Please make sure PySAM isinstalled or use alternative input.")
        if value is None or isinstance(value, VariantFile):
            return value
        try:
            logging.debug(f"VCFFile: Reading variant info from {value}")
            return VariantFile(value)
        except Exception as e:
            logging.debug(e)
            self.fail(f"ERROR: Unable to open '{value}' as a VCF file.")



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
#       self.fail("Could not parse input. Please try a different file format.")

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


