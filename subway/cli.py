"""
cli interface for sub init and more
"""

import argparse  # click might be better, but as hpc app, we try our best to only use builtin module
import os
import sys
import json
import shutil
from functools import partial

from .bootstrap import env_init
from .utils import load_json, editor, print_json, ts2str, simple_template_render
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
        configparser = subparsers.add_parser(
            "config", aliases="c", description="config subway"
        )
        configparser.add_argument(dest="action", help="action on config")
        debugparser = subparsers.add_parser(
            "debug", aliases="d", description="debug related commands"
        )
        debugparser.add_argument(dest="object", help="object for debug")
        debugparser.add_argument(
            dest="action", help="action for debug", nargs="?", default=None
        )
        # TODO: automatic way to add help for subparser, eg. decorator of query funcs
        # TODO: plugable subcommands, eg slurm
        self.parser = parser
        if not _argv:
            _argv = sys.argv[1:]
        self.args = parser.parse_args(_argv)
        self.tree = None
        self._subway_path = os.path.dirname(__file__)

        for a in [
            "reason",
            "assoc",
            "prev",
            "next",
            "resource",
            "executable_version",
            "check_executable_version",
        ]:
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
            if self.args.command not in ["init", "i", "help", "h", "debug", "d"]:
                # there is no system independent elegant way to get root path in python
                # see https://stackoverflow.com/questions/17429044/constructing-absolute-path-with-os-path-join
                cp = self.args.dir
                # last path, current path
                while True:
                    if os.path.exists(os.path.join(cp, ".subway")):
                        self.dir = cp
                        break
                    lp = cp
                    cp = os.path.dirname(cp)
                    if cp == lp:  # confirm lp is root path
                        raise CLIException(
                            message="fatal: Not a subway project", code=14
                        )

                self.conf = load_json(os.path.join(self.dir, ".subway", "config.json"))
                self.history = load_json(
                    os.path.join(self.dir, ".subway", "history.json")
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
        os.system(os.path.join(self.dir, executer))

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
                self.dir, self.conf.get("inputs_dir", ""), self.jid
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
                self.dir, self.conf.get("outputs_dir", ""), self.jid
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
            editor(os.path.join(self.dir, ".subway", "config.json"))

    c = config

    def help(self):
        self.parser.print_help()

    h = help

    def _history_clean(self):
        with open(os.path.join(self.args.dir, ".subway", "history.json"), "w") as f:
            json.dump({}, f)

    def _render_run_check(self, runpath, checkpath=None, subwaypath=None):
        """

        :param runpath: relative path (only file name)
        :param checkpath:
        :param subwaypath: dir path for subway lib
        :return:
        """
        if not subwaypath:
            subwaypath = self._subway_path
        if checkpath:
            shutil.copyfile(
                os.path.join(subwaypath, "examples", "miscs", checkpath),
                os.path.join(self.args.dir, "check.py"),
            )
        shutil.copyfile(
            os.path.join(subwaypath, "examples", "miscs", runpath),
            os.path.join(self.args.dir, "run.py"),
        )

    def debug(self):
        if self.args.object == "history":
            if self.args.action in ["clear", "clean"]:
                self._history_clean()

        if self.args.object == "reinit":
            self._history_clean()
            self.conf = load_json(os.path.join(self.args.dir, ".subway", "config.json"))
            for p in [
                os.path.join(self.args.dir, self.conf["inputs_dir"]),
                os.path.join(self.args.dir, self.conf["outputs_dir"]),
                os.path.join(
                    self.args.dir, self.conf.get("check_inputs_dir", "cinputs")
                ),
                os.path.join(
                    self.args.dir, self.conf.get("check_outputs_dir", "coutputs")
                ),
            ]:
                if os.path.exists(p):
                    shutil.rmtree(p)
                os.mkdir(p)

        if self.args.object == "setup":
            if self.args.action == "rgd":
                conf = load_json(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_config.json"
                    )
                )
                env_init(self.args.dir, conf, include_main=False)
                var_dict = {"_py": sys.executable, "_sub": "RgDSub", "_chk": "RgDChk"}
                simple_template_render(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_main.template"
                    ),
                    os.path.join(self.args.dir, conf.get("entry_point", "main.py")),
                    var_dict,
                )
                self._render_run_check("rg_run.py", "rg_check.py")

            elif self.args.action == "rgs":
                conf = load_json(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_config.json"
                    )
                )
                env_init(self.args.dir, conf, include_main=False)
                var_dict = {"_py": sys.executable, "_sub": "RgSSub", "_chk": "RgSChk"}
                simple_template_render(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_main.template"
                    ),
                    os.path.join(self.args.dir, conf.get("entry_point", "main.py")),
                    var_dict,
                )
                self._render_run_check("rg_run.py")

            elif self.args.action == "rgl":
                conf = load_json(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_config.json"
                    )
                )
                env_init(self.args.dir, conf, include_main=False)
                var_dict = {"_py": sys.executable, "_sub": "RgSub", "_chk": "RgChk"}
                simple_template_render(
                    os.path.join(
                        self._subway_path, "examples", "miscs", "rg_main.template"
                    ),
                    os.path.join(self.args.dir, conf.get("entry_point", "main.py")),
                    var_dict,
                )
                self._render_run_check("rg_run.py")
            os.chmod(
                os.path.join(self.args.dir, conf.get("entry_point", "main.py")), 0o700
            )

    d = debug

    def _noid(self):
        raise CLIException("Please specify job id", code=12)
