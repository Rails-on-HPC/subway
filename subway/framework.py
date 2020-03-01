"""
Basic classes: submitter, checker and processor for subway main loop
"""

import os
import sys
import heapq
from abc import ABC, abstractmethod

from .utils import now_ts, md5file
from .config import history, conf, update_history, update_conf
from .exceptions import EndingBubble


class Checker(ABC):
    """
    Empty base abstract class for checker.
    """

    @abstractmethod
    def __call__(self):
        pass


class Submitter(ABC):
    """
    Empty base abstract class for submitter.
    """

    @abstractmethod
    def __call__(self):
        pass


class Processor(ABC):
    """
    Base class for processor
    """

    def __init__(self, pipeline=None, **kwargs):
        """

        :param pipeline: List[str]. List of str of method name that processor will run one by one.
        :param kwargs:
        """
        if not pipeline:
            pipeline = []
        self.pipeline = pipeline
        self.kws = kwargs

    def __call__(self):
        for func in self.pipeline:
            getattr(self, func)()


class PlainChk(Checker):
    """
    The very general checker class.
    """

    def __init__(self, params=None, **kwargs):
        """

        :param params: list of dict
        """
        self.kws = kwargs
        self.params = params

    def __call__(self):
        """
        `DIY: not recommended`.
        main process of checker.

        :return: None.
        """
        if not history:  ## preprocess for kickstart inputs file and history.json

            nfs = self.check_task()
            for nf, resource in nfs:
                self.post_new_input(nf, resource)

        else:
            running_fs = [f for f, s in history.items() if s["state"] == "running"]
            if not running_fs:
                print("no job is running", file=sys.stderr)
            for f in running_fs:
                if self.is_finished(f) or self.is_aborted(f):
                    history[f]["finishing_ts"] = self.finishing_time(f)
                    history[f]["state"] = (
                        "finished" if self.is_finished(f) else "aborted"
                    )
                    nfs = self.check_task(f)
                    if nfs:
                        assert (
                            len(nfs) == 1
                        )  # single job for check, one-one correspondence
                        history[f]["assoc"] = nfs[0][0]
                        history[f]["check_resource"] = nfs[0][1]
                    # for nf, resource in nfs:
                    #     self.post_new_input(nf, resource, f)

            checking_fs = [f for f, s in history.items() if s["state"] == "checking"]
            if not checking_fs:
                print("no job is checking", file=sys.stderr)
            for f in checking_fs:
                if self.is_checked(f):
                    nfs = self.check_task(f)
                    if history[f]["state"] != "frustrated":
                        # check_checking also has the right to label the job frustrated
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
                    if history[f]["state"] != "failed":
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
        ## check whether all tasks are finished, if yes exit main workflow
        end_states = ["failed", "resolved", "checked", "frustrated"]
        for j, s in history.items():
            if s["state"] not in end_states:
                break
        else:
            if not self.kws.get("test"):  # debug for pytest doesn't exit
                raise EndingBubble(message="all jobs are done")

    def post_new_input(self, jobid, resource=None, prev=None):
        """
        `DIY: not recommended.`
        Make some inplace changes on history dict after new task is generated,
        it is vital for history record system.
        This method is not recommended to customize in subclass of checker,
        at least, one should include it by ``super().post_new_input``.

        :param jobid: str. new job id.
        :param resource: Optional[Dict]. resource dict for the new job.
        :param prev: Optional[str]. Parent job id. Default None indicates no prev job.
        :return: None.
        """
        if prev:
            history[prev]["next"].append(jobid)
        history[jobid] = {}
        history[jobid]["state"] = "pending"
        history[jobid]["prev"] = prev
        history[jobid]["next"] = []
        history[jobid]["creating_ts"] = now_ts()
        if not resource:
            resource = {}
        history[jobid]["resource"] = resource
        # resource is in general a dict indicating specific computation resource for this task

    def check_task(self, jobid=None):
        """
        `DIY: not recommended.`
        Determine whether output is "converged" and if not, generate new input files for more calculation
        with the new jobid and resource returned.
        The inner process will dispatch to :py:meth:`check_finished`, :py:meth:`check_aborted`
        :py:meth:`check_checking`, :py:meth:`check_resolving`.

        :param jobid: Optional[str, None]. Default None means kickstart generation for inputs tasks.
        :return: List[Tuple[str, Dict]]. [(next jobid, resource dict)]
        """
        # jobid = None for kickstart,
        # jobid state can be:
        # finished (to generate check input and check id -> checked),
        # aborted (to generate analyse input and check id -> analysed)
        # checked (to generate main input and new id, -> ended)
        # analysed (to generate main input and new id, -> resolved/failed)

        r = None  # [()]
        if not jobid:
            r = self.check_kickstart()
            return r

        s = history[jobid]["state"]

        # if s == "finished":
        #     r = self.check_finished(jobid)
        # elif s == "aborted":
        #     r = self.check_aborted(jobid)
        # elif s == "checking":
        #     r = self.check_checking(jobid)
        # elif s == "resolving":
        #     r = self.check_resolving(jobid)

        if s in ["finished", "aborted", "checking", "resolving"]:
            r = getattr(self, "check_" + s)(jobid)
        else:
            raise ValueError("check_task doesn't support job state %s" % s)
            # TODO: change to subway exceptions?
        return r

    def check_finished(self, jobid):
        """
        `DIY: depends.`
        Check job whose state is ``finished``.
        Namely, the main task has been computed sucessfully,
        we need to check output of main task to further
        generate check job and associated check input.
        On the other hand, if there is no need for check job
        to be controlled by submitter (i.e. one simply check
        the main output in checker and generate new jobs),
        one can omit this method, since the default implementation
        is used for such case (no check job scenario).

        :param jobid: str.
        :return: List[Tuple[str, Dict]]. The length of the list must be
            0 (no check job) or
            1 (namely check job must be one to one correspondence with main job).
        """
        history[jobid]["state"] = "checking"
        history[jobid]["checking_ts"] = now_ts()
        # skip check job submit, check them directly
        return []

    def check_aborted(self, jobid):
        """
        `DIY: depends.`
        Check job whose state is ``aborted``.
        These jobs failed the main task, and this method
        should generate resolve task and resolve input if necessary.
        If resolve job is not under control of submitter,
        the default implementation is ok.

        :param jobid: str.
        :return: List[Tuple[str, Dict]]. The length of the list must be 0 or 1.
        """
        history[jobid]["state"] = "resolving"
        history[jobid]["checking_ts"] = now_ts()
        return []

    def check_kickstart(self):
        """
        `DIY: strongly recommended.`
        Generate jobs with inputs at the beginning.
        The default impl does nothing. If the user doesn't define this method
        in subclass, then the user must add inputs files and possible items
        in empty history.json by hand.

        :return: List[Tuple[str, Dict]]. [(jobid, resource dict)]
        """
        return []

    @abstractmethod
    def check_checking(self, jobid):
        """
        `DIY: must.`
        Check job whose state is ``checking``.
        Jobs are sent to this method only when :py:meth:`is_checked` returns ``True``.
        Generate possible new jobs and inputs based on results from main task
        and possibly check task. The very core of checker class.

        :param jobid: str.
        :return: List[Tuple[str, Dict]]. [(jobid, resource dict), ...]
        """
        return []

    def check_resolving(self, jobid):
        """
        `DIY: depends.`
        Check job whose state is ``resolving``.
        Jobs are sent to this method only when :py:meth:`is_resolved` returns ``True``.
        If the user case has no consideration on error tolerant and aborted states,
        the method can be left as it is doing nothing.

        :param jobid: str.
        :return: List[Tuple[str, Dict]]. [(jobid, resource dict), ...]
        """
        return []

    def is_finished(self, jobid):
        """
        `DIY: strongly recommended.`
        Whether a ``running`` task is finished.
        The default impl is to check whether output file exists.
        It is not a good criteria for finished job in most cases.

        :param jobid: str.
        :return:
        """
        outputs_abs_dir = conf.get("outputs_abs_dir")
        if outputs_abs_dir and os.path.exists(outputs_abs_dir):
            output_fs = [
                f
                for f in os.listdir(outputs_abs_dir)
                if os.path.isfile(os.path.join(conf["outputs_abs_dir"], f))
            ]
            return jobid in output_fs
        return True

    def is_aborted(self, jobid):
        """
        `DIY: depends.`
        Whether a ``running`` task is failed.

        :param jobid: str.
        :return: bool.
        """
        return False

    def is_checked(self, jobid):
        """
        `DIY: depends.`
        Whether a ``checking`` task is finished.

        :param jobid: str.
        :return: bool.
        """
        return True

    def is_frustrated(self, jobid):
        """
        `DIY: depends.`
        Whether a ``checking`` task is failed.

        :param jobid: str.
        :return: bool.
        """
        return False

    def is_resolved(self, jobid):
        """
        `DIY: depends.`
        Whether a ``resolving`` task is finished.

        :param jobid: str.
        :return: bool.
        """
        return True

    def is_failed(self, jobid):
        """
        `DIY: depends.`
        Whether a ``resolving`` task is failed.

        :param jobid: str.
        :return: bool.
        """
        return False

    def finishing_time(self, jobid):
        """
        `DIY: depends.`
        This method is reponsible for 2 states: ``finished`` and ``aborted``.
        The default impl for ``finished`` state is last modifed time of output file.

        :param jobid: str.
        :return: float. timestamp.
        """
        if history[jobid]["state"] == "finished":
            outputs_abs_dir = conf.get("outputs_abs_dir")
            if outputs_abs_dir and os.path.exists(
                os.path.join(conf["outputs_abs_dir"], jobid)
            ):
                return os.path.getmtime(os.path.join(conf["outputs_abs_dir"], jobid))
            return now_ts()
        elif history[jobid]["state"] == "aborted":
            return now_ts()

    def ending_time(self, jobid):
        """
        `DIY: depends.`
        This method is reponsible for 4 states:
        ``checked``, ``resolved``, ``frustrated``, ``failed``.
        The default impl is now.

        :param jobid: str.
        :return: float. timestamp.
        """
        return now_ts()


## creating_ts pending beginning_ts running finishing_ts finished checking_ts checking  ending_ts checked/frustrated
##                                                       aborted checking_ts resolving  ending_ts resolved/failed
class PlainSub(Submitter):
    """
    The very general submitter class.
    """

    def __init__(self, **kwargs):
        self.pending_queue = []
        self.finished_queue = []
        self.aborted_queue = []
        self.is_queue = False
        self.kws = kwargs

    def __call__(self):
        """
        `DIY: not recommend.`

        :return:
        """
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
                if conf.get("executable_version"):
                    history[t]["executable_version"] = conf["executable_version"]
            elif history[t]["state"] == "finished":
                history[t]["state"] = "checking"
                history[t]["checking_ts"] = now_ts()
                if conf.get("check_executable_version"):
                    history[t]["check_executable_version"] = conf[
                        "check_executable_version"
                    ]
            elif history[t]["state"] == "aborted":
                history[t]["state"] = "resolving"
                history[t]["checking_ts"] = now_ts()
                if conf.get("check_executable_version"):
                    history[t]["check_executable_version"] = conf[
                        "check_executable_version"
                    ]
            else:
                raise ValueError("submit job doesn't support job state %s" % s)

        update_history()

    def priority_task(self):
        """
        `DIY: depends.`
        The default impl prefer jobs in aborted state, then finished state and finally pending state.
        Plus, the default impl prefer older jobs.
        choose the first task to be run from pending, finished and aborted queue

        :return: str, jobid.
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
        `DIY: depends.`
        The default impl is ok if you only want to restrict some resource in simple and soft way.
        check the restriction is ok for now with all running tasks in consideration.

        :return: bool. whether the total resource limit is reached.
        """
        # the default pattern: for each job, possible keys are *_count in history resource or check_resource
        # compare these with items *_limit in resource_limit in config
        resource_status = {}
        for j, s in history.items():
            if s["state"] == "running":
                for k, v in s.get("resource", {}).items():
                    if k.endswith("_count"):  # eg. cpu_count: 2
                        resource_status[k] = resource_status.get(k, 0) + v
            elif s["state"] in ["checking", "resolving"]:
                for k, v in s.get("check_resource", {}).items():
                    if k.endswith("_count"):  # eg. cpu_count: 2
                        resource_status[k] = resource_status.get(k, 0) + v
        for res_count, usage in resource_status.items():
            if res_count[:-5] + "limit" in conf.get("resource_limit", {}):
                if conf["resource_limit"][res_count[:-5] + "limit"] <= usage:
                    return True  ## some usage has already bypass the limit
        return False  ## no resource limitation
        # note the implementation here is for soft resource limit, since job ends only when limit is over

    def submit_job(self, jobid):
        """
        `DIY: not recommend`.
        submit job, for example, generate sbatch file and submit it to slurm.
        This method automaticall dispatch to :meth:`submit_pending`, :meth:`submit_finished` and :meth:`submit_aborted`.
        
        :param jobid: str.
        :return: None.
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
        """
        `DIY: must.`
        The very core of submitter class. It describes how do you define submitting a job.

        :param jobid: str.
        :return:
        """
        pass

    def submit_finished(self, jobid):
        """
        `DIY: depends.`
        If you have to deal with DS scheme as in :ref:`dsss`, then you must implement this method.

        :param jobid: str.
        :return:
        """
        pass

    def submit_aborted(self, jobid):
        """
        `DIY: depends.`
        If you have to deal with DS scheme as in :ref:`dsss` together with fault tolerance, then you must implement this method.

        :param jobid: str.
        :return:
        """
        pass


class PreProcessor(Processor):
    def version_check(self):
        """
        Must also include :meth:`update_conf` into the ``pipeline``.
        Lock the binary version with hashing, ensure different binary cannot be run
        unless the version is changed in ``config.json``/

        :return: None
        """
        if self.kws.get("version_checking_path"):
            cp = self.kws.get("version_checking_path")
            # [(relative path, version number)]
        else:
            cp = []
            for k, v in conf.items():
                if k.endswith("executable") and conf.get(k + "_version"):
                    cp.append((v, conf[k + "_version"]))

        conf.setdefault("hashing", {})
        # hashing: {"main.o": {"1.0.0": "md5agsdhj"}}
        for p in cp:
            conf["hashing"].setdefault(p[0], {})
            f = os.path.join(conf["work_dir"], p[0])
            if os.path.exists(f):
                nhash = md5file(f)
                ohash = conf["hashing"].get(p[0], {}).get(p[1])
                if ohash:
                    assert (
                        nhash == ohash
                    )  # TODO: the exception is to be wrapped in a better presentation
                conf["hashing"][p[0]][p[1]] = nhash

    @staticmethod
    def conf_update():
        """
        Write ``conf`` in memory back to ``config.json``.

        :return: None.
        """
        update_conf()
