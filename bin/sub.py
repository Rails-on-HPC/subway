import sys
import os

subpypath = os.path.abspath(__file__)
binpath = os.path.dirname(subpypath)
subwaypath = os.path.dirname(binpath)
sys.path.insert(0, subwaypath)

from subway import cli

cli.cli()
