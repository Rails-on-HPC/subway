import sys

inputfile = sys.argv[1]
outputfile = sys.argv[2]

if __name__ == "__main__":
    with open(inputfile, "r") as f:
        l, r = f.readlines()
        l = float(l)
        r = float(r)

    b = r - l

    with open(outputfile, "w") as f:
        f.writelines([str(b)])
