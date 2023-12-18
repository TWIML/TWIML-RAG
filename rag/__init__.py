import sys; sys.path.append("..")
from os.path import dirname; 

module_path = dirname(dirname(__file__)) # top-level `rag` folder
src_path = dirname(__file__) # nested `rag` folder

from rag.setup import run_setup; run_setup()