Quick Start
=============

Installation
--------------

Install subway in one of the following approaches

- ``pip install hpcsubway``

- ``git clone . https://github.com/Rails-on-HPC/subway.git && python setup.py install``

- ``git clone . https://github.com/Rails-on-HPC/subway.git && export $SUBWAY_PATH=$(pwd)/bin``


For the third approach, you don't need to install things at all,
which might be prefect for HPC setups.

**Support platforms:** subway is compatible with python 3.5 to 3.8 in linux and macos.


Workflow for a subway project
----------------------------------------------

1. Just ``subway init`` in the empty project folder.

2. Then you can copy your program binaries into this folder.

3. Modify configurations by ``subway config edit`` for this project. See :ref:`config.json`.

4. Probably you may need to add some template files.

5. Write your own ``main.py`` as ``entry_point`` of the project.

6. Now ``subway run`` to get everything running. (You can also submit ``subway run`` to task managers like slurm)

7. Analyse the results by powerful ``subway query`` command.


Writting entry point py
------------------------

The entry point of the project, often named as ``main.py``, is the engine and monitor of the whole project,
which is also the underlying executable when ``subway run``.

If you initialize subway project by `subway init`, then a ready to go template of ``main.py`` has already been in the project folder.

The file demo is as follows:

.. code-block:: python

    #! /usr/bin/python

    import os

    from subway import cons

    cons.work_dir = os.path.dirname(os.path.abspath(__file__))

    from subway.config import conf, history

    from subway.workflow import main_once, main_rt

    from subway.plugins import DebugSub, DebugChk


    if __name__ == "__main__":
        main_rt(DebugChk(), DebugSub())


The ingredients include:

1. Shebang in the first line, change it to your python path

2. The following several lines setup ``work_dir`` variable, you should keep them as they are.

3. Import what you may need from subway, such as ``conf``, ``history``, as well as main loop function ``main_rt``, together with checker and submitter classes you want to customize.

4. Implement your own checker and submitter if needed.

5. Run ``main_rt`` with your checker and submitter as arguments.


Also note the file must have executable permission which can be set by ``chmod +x main.py``.

