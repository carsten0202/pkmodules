
# Import functions from click that we want to make available upstairs
from click import *

# Then import the functions from pkclick that we want to replace those in click
from .pkclick import *

