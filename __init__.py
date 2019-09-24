import sys
from pathlib import Path

dirpath = Path(__file__).resolve().parent
syspath = dirpath / 'libraswap'
sys.path.append(syspath)
