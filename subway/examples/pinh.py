import os
import math
from ..plugins import NHSChk, NHSSub
from ..config import conf, history
from ..htree import HTree


class PiNSub(NHSSub):
    pass


class PiNChk(NHSChk):
    def check_checking_main(self, jobid):
        n = 1
        tr = HTree(history)
        job_trace = []
        job_trace.append(jobid)
        while tr.parent(jobid, n):
            jobid = tr.parent(jobid, n)
            job_trace.append(jobid)
        tot4 = 0
        tot = 0
        for j in job_trace:
            with open(os.path.join(conf["outputs_abs_dir"], j), "r") as f:
                pi, times = f.readlines()
                pi = float(pi)
                times = float(times)
            tot4 += pi / 4 * times
            tot += times
        ratio = tot4 / tot
        std = 4 * math.sqrt(ratio * (1 - ratio)) / math.sqrt(tot)
        print("the deviation now is %s" % std)
        if std > 0.01:
            return [[2000]]
        else:
            print("pi estimation has been converged: the result is %s" % (ratio * 4))
            return []
