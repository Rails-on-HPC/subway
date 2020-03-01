"""
Forest of multiple trees of tasks
"""

from .exceptions import MatchError


class HTree:
    """
    Trees structure for tasks recorded in history.json.
    """

    def __init__(self, history):
        self.history = history
        self.roots_list = None
        self.leaves_list = None

    def match(self, idprefix):
        results = []
        for j, _ in self.history.items():
            if j.startswith(idprefix):
                results.append(j)
        if not results:
            raise MatchError("Job id prefix matches no job")
        if len(results) > 1:
            raise MatchError("Job id prefix matches multiple jobs")
        return results[0]

    def parent(self, jobid, n=1):
        """
        n-level parent task id

        :param jobid:
        :param n: n<=0 for the ultimate root
        :return:
        """
        p1 = self.history[jobid]["prev"]
        # print(p1)
        if p1 is None:
            if n > 0:
                return
                # raise ValueError("%s has no parent in that level" % jobid)
            else:
                return jobid
        if n == 1:
            return p1
        return self.parent(p1, n - 1)

    def roots(self):
        """
        Find all jobs with no parent.

        :return: List[str]. jobid list
        """
        if self.roots_list is not None:
            return self.roots_list
        r = []
        for jid, s in self.history.items():
            if s["prev"] is None:
                r.append(jid)
        self.roots_list = r
        return r

    def root(self, jobid):
        return self.parent(jobid, n=0)

    def children(self, jobid, n=1):
        """

        :param jobid: jobid or jobids list
        :param n: n=0 for the lowest level
        :return: list of children jobid
        """
        c1s = []
        if type(jobid) is not list:
            jobid = [jobid]
        for j in jobid:
            c1 = self.history[j]["next"]
            if c1:
                c1s.extend(c1)
        if n == 1:
            return c1s
        if not c1s and n <= 0:
            return jobid
        return self.children(c1s, n - 1)

    def end(self, jobid):
        """
        downstream of jobid as leaves

        :param jobid:
        :return: list
        """
        r = []
        for node in self.DFSvisit(jobid):
            if not self.history[node]["next"]:
                r.append(node)
        return r

    def DFSvisit(self, jobid):
        """
        generator yield job by DFS across the tree rooted as ``jobid``

        :param jobid: str.
        :yield: Next job id by DFS.
        """
        yield jobid
        for nid in self.history[jobid]["next"]:
            yield from self.DFSvisit(nid)

    def BFSvisit(self, jobid):
        pass  # TODO: BFS

    def leaves(self):
        if self.leaves_list is not None:
            return self.leaves_list
        l = []
        for jid, s in self.history.items():
            if not s["next"]:
                l.append(jid)
        self.leaves_list = l
        return l

    def print_tree(self, jobid, file=None, _prefix="", _last=True, _show=0):
        """
        print a tree to stdout with root as ``jobid``

        :param jobid: str.
        :param file: args for ``file=`` in ``print``. Default None to stdout.
        :param _prefix:
        :param _last:
        :param _show:
        :return:
        """
        print(
            _prefix,
            "`- " if _last else "|- ",
            jobid if _show == 0 else jobid[:_show],
            sep="",
            file=file,
        )
        _prefix += "   " if _last else "|  "
        children = self.history[jobid]["next"]
        child_count = len(children)
        for i, child in enumerate(children):
            _last = i == (child_count - 1)
            self.print_tree(child, file, _prefix, _last, _show)

    def print_trees(self, jobids, file=None, _prefix="", _last=True, _show=0):
        for jobid in jobids:
            self.print_tree(jobid, file, _prefix, _last, _show)
