"""
cli interface for sub init and more
"""

import argparse  # click might be better, but as hpc app, we try our best to only use builtin module
import os
import sys
import json

from .bootstrap import env_init
from .utils import load_json
from .htree import HTree


class SubwayCLI:
    def __init__(self):
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
        queryparser.add_argument(dest="path", help="the task investigated")
        queryparser.add_argument(dest="action", help="query action for task")

        self.parser = parser
        self.args = parser.parse_args(sys.argv[1:])
        self.conf = load_json(os.path.join(self.args.dir, ".subway", "config.json"))
        self.history = load_json(os.path.join(self.args.dir, ".subway", "history.json"))
        self.tree = None

    def __call__(self):
        getattr(self, self.args.command, "help")()

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
        match = []
        path = self.args.path
        for jobid, _ in self.history.items():
            if jobid.startswith(path):
                match.append(jobid)

        if not match:
            print("no matched task, please recheck the job id", file=sys.stderr)
            return
        elif len(match) > 1:
            print(
                "cannot determine unique jobid, please give longer job id sequence",
                file=sys.stderr,
            )
            return
        jobid = match[0]
        print("matched job id is %s" % jobid, file=sys.stderr)
        if self.args.action == "input":
            with open(
                os.path.join(self.args.dir, self.conf["inputs_dir"], jobid), "r"
            ) as f:
                content = f.readlines()
            print("".join(content))
        elif self.args.action == "output":
            with open(
                os.path.join(self.args.dir, self.conf["outputs_dir"], jobid), "r"
            ) as f:
                content = f.readlines()
            print("".join(content))
        elif self.args.action == "info":
            print(json.dumps(self.history[jobid], indent=2))
        elif self.args.action == "origin":
            print(self.tree.root(jobid))
        elif self.args.action == "end":
            print(self.tree.end(jobid))
        else:
            print(self.history[jobid][self.args.action])

    def help(self):
        self.parser.print_help()


cli = SubwayCLI()
