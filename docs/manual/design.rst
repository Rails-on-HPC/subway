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