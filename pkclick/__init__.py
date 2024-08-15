
# Import functions from click that we want to make available upstairs
from click import *

# Then import the functions from pkclick that we want to replace those in click
from .pkclick import *

# Finally inport from loose files:
from .BED3    import BED3
from .CSViter import CSViter
from .CSVlist import CSVlist
from .VCFFile import VCFFile