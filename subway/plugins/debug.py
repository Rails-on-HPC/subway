from ..framework import PlainChk, PlainSub


class DebugChk(PlainChk):
    def __init__(self, is_next=False):
        self.is_next = is_next

    def check_output(self, outputpath):
        print("the output path to be checked is %s" % outputpath)
        if self.is_next is True:
            from uuid import uuid1

            return [(str(uuid1()), {"core": 2})]
        return []


class DebugSub(PlainSub):
    def submit_job(self, inputpath):
        print("the input path to be submitted as job is %s" % inputpath)
        return
