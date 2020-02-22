"""
cli interface for sub init and more
"""

import argparse  # click might be better, but as hpc app, we try our best to only use builtin module
import os
import sys
import json
from functools import partial

from .bootstrap import env_init
from .utils import load_json, editor, print_json
from .htree import HTree
from .exceptions import CLIException


class SubwayCLI:
    def __init__(self, _argv=None):
        parser = argparse.ArgumentParser(description="subway is comming...")
        parser.add_argument(
            "-d", "--directory", dest="dir", default=os.getcwd(), help="project dir"
        )
        subparsers = parser.add_subparsers(dest="command")
        # init params
        initparser = subparsers.add_parser("init", description="init subway project")
        initparser.add_argument(
            "-c", "--config", dest="conf", default=None, help="config.json path"
        )
        # help params
        helpparser = subparsers.add_parser("help", description="help on subway")
        # run params
        runparser = subparsers.add_parser("run", description="check and submit jobs")
        # query params
        queryparser = subparsers.add_parser(
            "query", description="query information on jobs"
        )
        queryparser.add_argument(
            "-j", "--job", dest="path", default=None, help="the task investigated"
        )
        queryparser.add_argument(dest="action", help="query action for task")
        configparser = subparsers.add_parser("config", description="config subway")
        configparser.add_argument(dest="action", help="action on config")
        self.parser = parser
        if not _argv:
            _argv = sys.argv[1:]
        self.args = parser.parse_args(_argv)
        self.conf = load_json(os.path.join(self.args.dir, ".subway", "config.json"))
        self.history = load_json(os.path.join(self.args.dir, ".subway", "history.json"))
        self.tree = None

        for k in [
            "pending",
            "running",
            "finished",
            "aborted",
            "checking",
            "resolving",
            "checked",
            "frustrated",
            "failed",
            "resolved",
        ]:
            self._meta_query_key(k)

    def __call__(self):
        try:
            getattr(self, self.args.command, "help")()
        except CLIException as e:
            print(e.message, file=sys.stderr)
            exit(e.code)

    def init(self):

        if self.args.conf is not None:
            with open(self.args.conf, "r") as f:
                conf = json.load(f)
        else:
            conf = None

        env_init(self.args.dir, conf)

        print(
            "the subway project has been successfully initialized in %s" % self.args.dir
        )

    def run(self):

        executer = self.conf.get("entry_point", "main.py")
        os.system(os.path.join(self.args.dir, executer))

    def query(self):
        if not self.tree:
            self.tree = HTree(self.history)
        self.jid = self.args.path
        if self.jid:
            self.jid = self.tree.match(self.jid)
            # print(self.jid)
            print("matched job id is %s" % self.jid, file=sys.stderr)
        return getattr(self, "query_" + self.args.action, "query_info")()

    def query_info(self):
        if self.jid:
            print_json(self.history[self.jid])
        else:
            print_json(self.history)

    def query_tree(self):
        if self.jid:
            self.tree.print_tree(self.jid)
        else:
            self.tree.print_trees(self.tree.roots())

    def query_input(self):
        if self.jid:
            inputpath = os.path.join(
                self.args.dir, self.conf.get("inputs_dir", ""), self.jid
            )
            if os.path.exists(inputpath):
                with open(inputpath, "r") as f:
                    content = f.readlines()
                print("".join(content))
            else:
                raise CLIException("no input files for %s" % self.jid)
        else:
            self._noid()

    def query_output(self):
        if self.jid:
            outputpath = os.path.join(
                self.args.dir, self.conf.get("outputs_dir", ""), self.jid
            )
            if os.path.exists(outputpath):
                with open(outputpath, "r") as f:
                    content = f.readlines()
                print("".join(content))
            else:
                raise CLIException("no output files for %s" % self.jid)
        else:
            self._noid()

    def query_root(self):
        if self.jid:
            print(self.tree.root(self.jid))
        else:
            print(*self.tree.roots(), sep="\n")

    def query_next(self):
        if self.jid:
            n = self.history[self.jid]["next"]
            print(*n, sep="\n")
        else:
            self._noid()

    def query_prev(self):
        if self.jid:
            p = self.history[self.jid]["prev"]
            print(p)
        else:
            self._noid()

    def query_leaves(self):
        if self.jid:
            print(*self.tree.end(self.jid), sep="\n")
        else:
            print(*self.tree.leaves(), sep="\n")

    def query_state(self):
        if self.jid:
            print(self.history[self.jid]["state"])
        else:
            s = set()
            for _, st in self.history.items():
                s.add(st["state"])
            print(*s, sep="\n")

    def _meta_query_key(self, key):
        """
        meta function to generate member function for this class, generate function as follows
        # def query_checked(self):
        #     if self.jid:
        #         print("1" if self.history[self.jid]['state'] == "checked" else "0")
        #     else:
        #         r = []
        #         for j, s in self.history.items():
        #             if s['state'] == "checked":
        #                 r.append(j)
        #         print(*r, sep="\n")

        :param key:
        :return:
        """

        def f(s):
            if s.jid:
                print("1" if self.history[self.jid]["state"] == key else "0")
            else:
                r = []
                for j, d in s.history.items():
                    if d["state"] == key:
                        r.append(j)
                print(*r, sep="\n")

        setattr(self, "query_" + key, partial(f, self))

    def config(self):
        if self.args.action == "show":
            print_json(self.conf)
        elif self.args.action == "edit":
            editor(os.path.join(self.args.dir, ".subway", "config.json"))

    def help(self):
        self.parser.print_help()

    def _noid(self):
        raise CLIException("Please specify job id", code=12)
