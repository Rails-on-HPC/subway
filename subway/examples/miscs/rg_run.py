import sys
from random import random

inputfile = sys.argv[1]
outputfile = sys.argv[2]

if __name__ == "__main__":
    with open(inputfile, "r") as f:
        L, l = f.readlines()
        L = float(L)
        l = float(l)

    r = L * random()

    with open(outputfile, "w") as f:
        f.writelines([str(r)])
