"""
cli interface for sub init and more
"""

import argparse  # click might be better, but as hpc app, we try our best to only use builtin module
import os
import sys
import json
from functools import partial

from .bootstrap import env_init
from .utils import load_json, editor, print_json, ts2str
from .htree import HTree
from .exceptions import CLIException, NoAttribute


class SubwayCLI:
    def __init__(self, _argv=None):
        parser = argparse.ArgumentParser(description="subway is comming...")
        parser.add_argument(
            "-d", "--directory", dest="dir", default=os.getcwd(), help="project dir"
        )
        subparsers = parser.add_subparsers(dest="command")
        # init params
        initparser = subparsers.add_parser(
            "init", aliases="i", description="init subway project"
        )
        initparser.add_argument(
            "-c", "--config", dest="conf", default=None, help="config.json path"
        )
        # help params
        helpparser = subparsers.add_parser(
            "help", aliases="h", description="help on subway"
        )
        # run params
        runparser = subparsers.add_parser(
            "run", aliases="r", description="check and submit jobs"
        )
        # query params
        queryparser = subparsers.add_parser(
            "query", aliases="q", description="query information on jobs"
        )
        queryparser.add_argument(
            "-j", "--job", dest="path", default=None, help="the task investigated"
        )
        queryparser.add_argument(dest="action", help="query action for task")
        configparser = subparsers.add_parser("config", description="config subway")
        configparser.add_argument(dest="action", help="action on config")
        debugparser = subparsers.add_parser(
            "debug", aliases="d", description="debug related commands"
        )
        debugparser.add_argument(dest="object", help="object for debug")
        debugparser.add_argument(dest="action", help="action for debug")
        # TODO: automatic way to add help for subparser, eg. decorator of query funcs
        # TODO: plugable subcommands, eg slurm
        self.parser = parser
        if not _argv:
            _argv = sys.argv[1:]
        self.args = parser.parse_args(_argv)
        self.tree = None

        for a in ["reason", "assoc", "prev", "next"]:
            self._meta_query_attr(a)

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

        for t in [
            "creating",
            "beginning",
            "finishing",
            "checking",
            "ending",
            "beginning_real",
        ]:
            self._meta_query_ts(t)

    def __call__(self):
        try:
            if self.args.command not in ["init", "help"]:
                self.conf = load_json(
                    os.path.join(self.args.dir, ".subway", "config.json")
                )
                self.history = load_json(
                    os.path.join(self.args.dir, ".subway", "history.json")
                )
            # conf cannot load for init
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

    i = init

    def run(self):

        executer = self.conf.get("entry_point", "main.py")
        os.system(os.path.join(self.args.dir, executer))

    r = run

    def query(self):
        if not self.tree:
            self.tree = HTree(self.history)
        self.jid = self.args.path
        if self.jid:
            self.jid = self.tree.match(self.jid)
            # print(self.jid)
            print("matched job id is %s" % self.jid, file=sys.stderr)
        return getattr(self, "query_" + self.args.action, self.query_info)()

    q = query
    # beginning_real_ts, reason, assoc

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

    query_t = query_tree

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

    query_i = query_input

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

    query_o = query_output

    def query_root(self):
        if self.jid:
            print(self.tree.root(self.jid))
        else:
            print(*self.tree.roots(), sep="\n")

    query_r = query_root

    def query_leaves(self):
        if self.jid:
            print(*self.tree.end(self.jid), sep="\n")
        else:
            print(*self.tree.leaves(), sep="\n")

    query_l = query_leaves

    def query_state(self):
        if self.jid:
            print(self.history[self.jid]["state"])
        else:
            s = set()
            for _, st in self.history.items():
                s.add(st["state"])
            print(*s, sep="\n")

    query_s = query_state

    def _meta_query_attr(self, key):
        def f(s):
            if s.jid:
                v = self.history[self.jid].get(key, "")
                if isinstance(v, list):
                    print(*v, sep="\n")
                else:
                    print(v)
            else:
                s._noid()

        setattr(self, "query_" + key, partial(f, self))

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

    def _meta_query_ts(self, tstype):
        def f(s, readable=True):
            if s.jid:
                ts = self.history[s.jid].get(tstype + "_ts", "")
                if ts:
                    if readable:
                        ts = ts2str(ts)
                    print(ts)
                else:
                    raise NoAttribute("no %s timestamps for %s" % (tstype, self.jid))
            else:
                self._noid()

        pfstr = partial(f, self, True)
        pfts = partial(f, self, False)
        # setattr(self, "query_" + tstype, pfstr) # may be conflict to state search
        setattr(self, "query_" + tstype + "_ts", pfts)
        setattr(self, "query_" + tstype + "_time", pfstr)

    def config(self):
        if self.args.action == "show" or self.args.action == "s":
            print_json(self.conf)
        elif self.args.action == "edit" or self.args.action == "e":
            editor(os.path.join(self.args.dir, ".subway", "config.json"))

    c = config

    def help(self):
        self.parser.print_help()

    h = help

    def debug(self):
        if self.args.object == "history":
            if self.args.action in ["clear", "clean"]:
                with open(
                    os.path.join(self.args.dir, ".subway", "history.json"), "w"
                ) as f:
                    json.dump({}, f)

    d = debug

    def _noid(self):
        raise CLIException("Please specify job id", code=12)
