import os
import sys
import json
import shlex
import subprocess
from datetime import datetime


def now_ts():
    return datetime.now().timestamp()


def load_json(conf_file):
    with open(conf_file, "r") as fp:
        conf_dict = json.load(fp)
    return conf_dict


def print_json(json_dict, indent=2):
    print(json.dumps(json_dict, indent=indent))


#: editors to try if VISUAL and EDITOR are not set
_default_editors = ["vim", "vi", "emacs", "nano"]


def which(binary, path=None):
    """
    Like ``which`` in shell
    """
    if not path:
        path = os.environ.get("PATH", "")

    if isinstance(path, str):
        path = path.split(os.pathsep)

    for directory in path:
        exe = os.path.join(directory, binary)
        if os.path.isfile(exe) and os.access(exe, os.X_OK):
            return exe

    return None


def editor(path, **kwargs):
    """
    Invoke the user's editor.
    This will try to execute the following, in order:
      1. $VISUAL <args>    # the "visual" editor (per POSIX)
      2. $EDITOR <args>    # the regular editor (per POSIX)
      3. some default editor (see ``_default_editors``) with <args>
    If an environment variable isn't defined, it is skipped.  If it
    points to something that can't be executed, we'll print a
    warning. And if we can't find anything that can be executed after
    searching the full list above, we'll raise an error.
    """
    # allow this to be customized for testing
    _run = kwargs.get("_run", subprocess.run)

    def try_exec(exe):
        """
        Try to execute an editor with ``subprocess.run``, and warn if it fails.

        :return: (bool) False if the editor failed, ideally does not
            return if ``run`` succeeds, and ``True`` if the
            ``run`` does return successfully.
        """
        try:
            _run(exe)
            return True

        except OSError as e:
            # Show variable we were trying to use, if it's from one
            print("Could not execute %s due to error:" % exe, str(e), file=sys.stderr)
            return False

    def try_env_var(var):
        """
        Find an editor from an environment variable and try to exec it.
        This will warn if the variable points to something is not
        executable, or if there is an error when trying to exec it.
        """
        if var not in os.environ:
            return False

        return try_exec(shlex.split(os.environ[var] + " " + path))

    # try standard environment variables
    if try_env_var("VISUAL"):
        return
    if try_env_var("EDITOR"):
        return

    # nothing worked -- try the default we can find
    for exe in _default_editors:
        if try_exec(shlex.split(which(exe) + " " + path)):
            return

    # Fail if nothing could be found
    print(
        "No text editor found! Please set the VISUAL and/or EDITOR "
        "environment variable(s) to your preferred text editor."
    )
