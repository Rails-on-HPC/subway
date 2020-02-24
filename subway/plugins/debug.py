from ..framework import PlainChk, PlainSub


class DebugChk(PlainChk):
    def __init__(self, params=None, is_next=False, **kwargs):
        self.is_next = is_next
        super().__init__(params=params, **kwargs)

    def check_checking(self, outputpath):
        print("the output path to be checked is %s" % outputpath)
        if self.is_next is True:
            from uuid import uuid1

            return [(str(uuid1()), {"core": 2})]
        return []


class DebugSub(PlainSub):
    def submit_pending(self, inputpath):
        print("the input path to be submitted as job is %s" % inputpath)
        return
