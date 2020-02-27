Design Philosophy
==================

|

- Keep everything

    Keep everything for later analysis, all inputs and outputs files,
    as well as submit scripts.
    It is worth noting that the common practice that only keep output files
    with file name as input parameters is not good enough and fail in many scenarios.

- Keep history

    To keep everything organized and easy for analysis, we keep all necessary informations
    for each job as a separate file ``history.json``.
    There is no need to directly access this file for normal user though.

- Organize tasks as trees

    An HPC project is a forest.
    Root jobs should develop children jobs when "converge condition" is not satisfied by check jobs.

- Manage projects with CLI interface

    From ``.subway`` directory to enhanced ``subway`` CLI utility,
    subway behaves somehow parallelling ``git``.


CLI utility
===========

The CLI command ``subway`` is ready to use if subway is install by ``pip`` or ``python setup.py install``.
If the users cannot or don't want to install subway via setup system, the package still works as standalone one.
To enable CLI support in this case, one need to:

    .. code-block:: bash

        export SUBWAY_PATH=/abspath/for/subway/bin
        export PATH=$SUBWAY_PATH:$PATH
        export SUBWAY_PYTHON=pythonyoulike

And ``subway`` command in shell is read to go!

The power of CLI tool is illustrated below:

    .. code-block:: bash

        $ subway -V
        subway version: 0.0.1
        $ subway init
        the subway project has been successfully initialized in <current dir>
        $ subway config edit
        # edit config.json
        # copy executables into the project and write up entry_point py script as the monitor
        $ subway run
        # the whole project is then running nonstopped, following the config and entry_point engine
        $ subway query -j 134 info
        # check detailed info of job with jobid starts with 134
        $ subway query -s "checking_tso<datetime(2020,2,2)"
        # search all jobs whose checking time if before 02/02/2020
        $ subway query -s "executable_version<>1.0.0; state=running"
        # search all jobs whose executable version is not 1.0.0 and the job is running
        $ subway query -s "resource.memory_count<=128"
        # search all jobs whole resource requirement on memory is no greater than 128
        $ subway query tree
        # print the job tree in the terminal
        $ subway query root
        # print all root jobs

There are more possibilies of CLI ``subway`` to be explored.


config.json
=============

The reserved configuration keys include:

- ``inputs_dir``, ``outputs_dir``: str, relpath. The default directories for input files and output files. The job submission scripts are also recommended in ``inputs_dir`` with ``.sh`` suffix.

- ``check_inputs_dir``, ``check_outputs_dir``: str, relpath. The directories for check job inputs and outputs if there are any. These options can be omitted is check tasks don't go through submitter.

- ``entry_point``: str, relpath. The engine py script for monitoring tasks, default as ``main.py``.

- ``executable``: str, relpath. The binary path for main task.

- ``check_executable``: str, relpath. The binary path for check task (if any).

- ``work_dir``: str, abspath. Dir path for this subway project.

- ``resource_limit``: Dict[str, Union[float, int]]. Keys with `_limit` as the end are treated as resource limitation.

- ``executable_version``, ``check_executable version``: str. Script versions for main and check executables.

Note all path above in config are relative path compared to ``work_dir``, which is the only absolute path.

There are also other keys used in different plugins as submitter and checker.

For example, :mod:`subway.plugins.sslurm` requires extra options, check plugin relavant documentations for more details:

- ``slurm_options``, ``check_slurm_options``: List[str]. Used in sbatch scripts, lines start with ``#SBATCH``.


history.json
=============

Keys in ``history.json`` are jobids, for each job, there is an information dict, the common keys include:

- ``prev``: str. The parent job id. None for root jobs.

- ``next``: List[str]. The children job ids. ``[]`` for leaves jobs.

- ``state``: str. Job state, legal values include: pending, running, finished, aborted, checking, resolving, checked, frustrated, resolved, failed.

- ``creating_ts``: float. Timestamps when the task is created, start of pending state.

- ``beginning_ts``: float. Timestamps when the task is submitted by the submitter, separating pending and running state.

- ``finishing_ts``: float. Timestamps when the main task of the job is finished, separating running state and finished/aborted state.

- ``checking_ts``: float. Timestamps when the associate check task begins running, separating finished and checking state, or separating aborted and resolving state.

- ``ending_ts``: float. Timestamps when the associate check task is finished and all the stuff are over for given job, separating checking state and checked/frustrated state, or separating resolving state and resolved/failed state.

- ``resource``: Dict[str, Any]. Storage for extra informations on the job. The most important ones are keys ends with ``_count``, these attributes are used to limit total computation resources.

- ``assoc``: str. Associated job id for check task of the job. In general check task share the same item with main task.

- ``check_resource``: Dict[str, Any]. resource dict for check task.

- ``executable_version``, ``check_executable_version``: str. Version information for binaries involved in the job.

Again, for plugins, more attributes are expected.  For example, :mod:`subway.plugins.sslurm`  has extra attributes in history.

- ``beginning_real_ts``: float. Timestamps, when the job is begin running from slurm.