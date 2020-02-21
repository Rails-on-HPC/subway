from abc import ABC, abstractmethod
import os
import heapq
from .utils import now_ts
from .config import history, conf, update_history


class Checker(ABC):
    """
    based on output path, check whether converge and give possibly next input files
    """

    def __init__(self):
        """
        """
        pass

    @abstractmethod
    def __call__(self):
        pass


class Submitter(ABC):
    """

    """

    def __init__(self):
        pass

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

            nfs = self.check_output()
            for nf, resource in nfs:
                self.post_new_input(nf, resource)

        else:

            output_fs = [
                f
                for f in os.listdir(conf["outputs_abs_dir"])
                if os.path.isfile(os.path.join(conf["outputs_abs_dir"], f))
                and self.is_finished(f)
            ]
            unchecked_fs = [f for f, s in history.items() if s["state"] == "running"]
            for f in unchecked_fs:
                if f in output_fs:
                    history[f]["finishing_ts"] = os.path.getmtime(
                        os.path.join(conf["outputs_abs_dir"], f)
                    )
                    nfs = self.check_output(
                        f
                    )  # check "converge" for new outputs and generate new input files if necessary
                    history[f]["state"] = "checked"
                    history[f]["checking_ts"] = now_ts()
                    for nf, resource in nfs:
                        self.post_new_input(nf, resource, f)
            else:
                print("no new finished file to be check")

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

    @abstractmethod
    def check_output(self, outputpath=None):
        """
        determine whether output is converged and if not, generate new input files for more calculation
        with the path and resource returned

        :param outputpath: relativepath (uuid string), if this is None, it means kickstart generation for inputs
        :return: [(nextfilename, resourcereuqired)]
        """
        return []

    def is_finished(self, outputpath):
        """
        This utils is to further distinguish those tasks that has incomplete outfile while still running

        :param outputpath: relativepath
        :return:
        """
        return True


## creating_ts pending beginning_ts running finishing_ts (finished) checking_ts checked
class PlainSub(Submitter):
    def __init__(self, resource_limit=None):
        self.resource_limit = resource_limit  ## dict here, {"job": 2}
        self.pending_queue = []
        self.is_pending_queue = False

    def __call__(self):
        self.is_pending_queue = False
        while not self.is_restricted():
            t = (
                self.priority_task()
            )  # TODO: considering priority and resource together to schedule, not into this recently
            if t is None:
                break
            self.submit_job(t)
            history[t]["state"] = "running"
            history[t]["beginning_ts"] = now_ts()

        update_history()

    def priority_task(
        self
    ):  ## choose the first task to be run from pending inputs queue, return relative filename for the inputs
        if self.is_pending_queue is False:
            for f, s in history.items():
                if s["state"] == "pending":
                    heapq.heappush(self.pending_queue, (s["creating_ts"], f))
            self.is_pending_queue = True
        if not self.pending_queue:
            return None
        return heapq.heappop(self.pending_queue)[1]  ## return the oldest input to run

    def is_restricted(
        self
    ):  ## check the restriction is ok for now with all running tasks in consideration
        return False  ## no resource limitation

    @abstractmethod
    def submit_job(
        self, inputpath
    ):  ## submit job, for example, generate sbatch file and submit it to slurm
        """

        :param inputpath: relative path (uuid string)
        :return:
        """
        pass
