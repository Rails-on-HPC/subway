from random import random
import sys


def pie(times=100):
    incircle = 0
    for _ in range(times):
        x = random()
        y = random()
        if x * x + y * y < 1:
            incircle += 1
    return incircle / times * 4


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        times = f.readlines()[0]
    p = pie(int(times))
    with open(sys.argv[2], "w") as f:
        f.writelines([str(p) + "\n" + times])
