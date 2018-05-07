# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # I know, it aint pretty
