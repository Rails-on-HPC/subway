from abc import ABC, abstractmethod
import os
import sys
import heapq
from .utils import now_ts
from .config import history, conf, update_history


class Checker(ABC):
    """
    based on output path, check whether converge and give possibly next input files
    """

    @abstractmethod
    def __call__(self):
        pass


class Submitter(ABC):
    """

    """

    @abstractmethod
    def __call__(self):
        pass


class PlainChk(Checker):
    def __init__(self, params=None):
        """

        :param params: list of dict
        """
        self.params = params

    def __call__(self):
        if not history:  ## preprocess for kickstart inputs file and history.json

            nfs = self.check_task()
            for nf, resource in nfs:
                self.post_new_input(nf, resource)

        else:
            running_fs = [f for f, s in history.items() if s["state"] == "running"]
            if not running_fs:
                print("no job is running", file=sys.stderr)
            for f in running_fs:
                if self.is_finished(f):
                    history[f]["finishing_ts"] = self.finishing_time(f)
                    history[f]["state"] = "finished"
                    self.check_task(f)
                    # check "converge" for new outputs and generate new input files if necessary

                    # for nf, resource in nfs:
                    #     self.post_new_input(nf, resource, f)
                elif self.is_aborted(f):
                    history[f]["state"] = "aborted"
                    history[f]["finishing_ts"] = self.finishing_time(f)
                    self.check_task(f)

            # else:
            #     print("no running job is finished or aborted", file=sys.stderr)

            checking_fs = [f for f, s in history.items() if s["state"] == "checking"]
            if not checking_fs:
                print("no job is checking", file=sys.stderr)
            for f in checking_fs:
                if self.is_checked(f):
                    nfs = self.check_task(f)
                    history[f]["state"] = "checked"
                    history[f]["ending_ts"] = self.ending_time(f)
                    for nf, resource in nfs:
                        self.post_new_input(nf, resource, f)
                elif self.is_frustrated(f):
                    history[f]["state"] = "frustrated"
                    history[f]["ending_ts"] = self.ending_time(f)
            # else:
            #     print("no checking job is finishing", file=sys.stderr)

            resolving_fs = [f for f, s in history.items() if s["state"] == "resolving"]
            if resolving_fs:
                print("some jobs are resolving", file=sys.stderr)
            for f in resolving_fs:
                if self.is_resolved(f):
                    nfs = self.check_task(f)
                    history[f]["state"] = "resolved"
                    history[f]["ending_ts"] = self.ending_time(f)
                    for nf, resource in nfs:
                        self.post_new_input(nf, resource, f)
                elif self.is_failed(f):
                    history[f]["state"] = "failed"
                    history[f]["ending_ts"] = self.ending_time(f)
            # else:
            #     print("no resolving job is finishing", file=sys.stderr)

        update_history()  # update history.json

    def post_new_input(self, inputpath, resource=None, prev=None):
        if prev:
            history[prev]["next"].append(inputpath)
        history[inputpath] = {}
        history[inputpath]["state"] = "pending"
        history[inputpath]["prev"] = prev
        history[inputpath]["next"] = []
        history[inputpath]["creating_ts"] = now_ts()
        if not resource:
            resource = {}
        history[inputpath]["resource"] = resource
        # resource is in general a dict indicating specific computation resource for this task

    def check_task(self, jobid=None):
        """
        determine whether output is converged and if not, generate new input files for more calculation
        with the path and resource returned

        :param outputpath: relativepath (uuid string), if this is None, it means kickstart generation for inputs
        :return: [(nextfilename, resourcereuqired)]
        """
        # jobid = None for kickstart, jobid state can be finished (to generate check input no new id -> checked),
        # aborted (to generate analyse input no new id -> analysed)
        # checked (to generate main input and new id, -> ended)
        # analysed (to generate main input and new id, -> resolved/failed)
        r = None  # [()]
        if not jobid:
            r = self.check_kickstart()
            return r

        s = history[jobid]["state"]

        if s == "finished":
            self.check_finished(jobid)
        elif s == "aborted":
            self.check_aborted(jobid)
        elif s == "checking":
            r = self.check_checking(jobid)
        elif s == "resolving":
            r = self.check_resolving(jobid)
        else:
            raise ValueError("check_task doesn't support job state %s" % s)
        return r

    def check_finished(self, jobid):
        history[jobid]["state"] = "checking"
        history[jobid]["checking_ts"] = now_ts()
        # skip check job submit, check them directly

    def check_aborted(self, jobid):
        history[jobid]["state"] = "resolving"
        history[jobid]["checking_ts"] = now_ts()

    def check_kickstart(self):
        return []

    @abstractmethod
    def check_checking(self, jobid):
        return []

    def check_resolving(self, jobid):
        return []

    def is_finished(self, jobid):
        """
        This utils is to further distinguish those tasks that has incomplete outfile while still running

        :param jobid: relativepath
        :return:
        """
        output_fs = [
            f
            for f in os.listdir(conf["outputs_abs_dir"])
            if os.path.isfile(os.path.join(conf["outputs_abs_dir"], f))
        ]
        return jobid in output_fs

    def is_aborted(self, jobid):
        return False

    def is_checked(self, jobid):
        return True

    def is_frustrated(self, jobid):
        return False

    def is_resolved(self, jobid):
        return True

    def is_failed(self, jobid):
        return False

    def finishing_time(self, jobid):
        """


        :param jobid:
        :return:
        """
        if history[jobid]["state"] == "finished":
            outputpath = os.path.join(conf["outputs_abs_dir"], jobid)
            if os.path.exists(outputpath):
                return os.path.getmtime(outputpath)
            return now_ts()
        elif history[jobid]["state"] == "aborted":
            return now_ts()

    def ending_time(self, jobid):
        """
        ending_time is reponsible for 4 states: checked resolved frustrated failed

        :param jobid:
        :return:
        """
        return now_ts()


## creating_ts pending beginning_ts running finishing_ts finished checking_ts checking  ending_ts checked/frustrated
##                                                       aborted checking_ts resolving  ending_ts resolved/failed
class PlainSub(Submitter):
    def __init__(self, resource_limit=None):
        self.resource_limit = resource_limit  ## dict here, {"job": 2}
        self.pending_queue = []
        self.finished_queue = []
        self.aborted_queue = []
        self.is_queue = False

    def __call__(self):
        self.is_queue = False  ## fix of realtime update for submitter
        while not self.is_restricted():
            t = self.priority_task()
            # TODO: considering priority and resource together to schedule, not into this recently
            if t is None:
                break
            self.submit_job(t)
            if history[t]["state"] == "pending":
                history[t]["state"] = "running"
                history[t]["beginning_ts"] = now_ts()
            elif history[t]["state"] == "finished":
                history[t]["state"] = "checking"
                history[t]["checking_ts"] = now_ts()
            elif history[t]["state"] == "aborted":
                history[t]["state"] = "resolving"
                history[t]["checking_ts"] = now_ts()
            else:
                raise ValueError("submit job doesn't support job state %s" % s)

        update_history()

    def priority_task(self):
        """
        choose the first task to be run from pending inputs queue

        :return: jobid
        """
        if self.is_queue is False:
            for f, s in history.items():
                if s["state"] == "pending":
                    heapq.heappush(self.pending_queue, (s["creating_ts"], f))
                elif s["state"] == "finished":
                    heapq.heappush(self.finished_queue, (s["finishing_ts"], f))
                elif s["state"] == "aborted":
                    heapq.heappush(self.aborted_queue, (s["finishing_ts"], f))
            self.is_queue = True
        if self.aborted_queue:
            return heapq.heappop(self.aborted_queue)[1]
        elif self.finished_queue:
            return heapq.heappop(self.finished_queue)[1]
        elif self.pending_queue:
            return heapq.heappop(self.pending_queue)[1]
        else:
            return

    def is_restricted(self):
        """
        check the restriction is ok for now with all running tasks in consideration

        :return:
        """

        return False  ## no resource limitation

    def submit_job(self, jobid):
        """
        submit job, for example, generate sbatch file and submit it to slurm
        
        :param jobid:
        :return:
        """
        s = history[jobid]["state"]
        if s == "pending":
            self.submit_pending(jobid)
        elif s == "finished":
            self.submit_finished(jobid)
        elif s == "aborted":
            self.submit_aborted(jobid)
        else:
            raise ValueError("submit job doesn't support job state %s" % s)
        pass

    @abstractmethod
    def submit_pending(self, jobid):
        pass

    def submit_finished(self, jobid):
        pass

    def submit_aborted(self, jobid):
        pass