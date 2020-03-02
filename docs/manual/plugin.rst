Plugins
========

Slurm
---------

For slurm plugin, we provide two levels of abstractions.

The lower level ones are :class:`subway.plugins.slurm.SlurmSub` and :class:`subway.plugins.slurm.SlurmChk`.

The higher level ones are :class:`subway.plugins.sslurm.SSlurmSub` and :class:`subway.plugins.sslurm.SSlurmChk`.
There are also DS scheme counterparts as :class:`subway.plugins.dslurm.DSlurmSub` and :class:`subway.plugins.dslurm.DSlurmChk`.

Lower-level utilities
~~~~~~~~~~~~~~~~~~~~~~~~

For the lower level checker and submitter, they are very similar with plainsub and plainchk, with only several enhanced methods
for timestamps generation and job finish bool.

For nomral user using slurm, we recommend the higher level abstraction classes which have better abstraction on job submitting and generations.

Architecture for sslurm
~~~~~~~~~~~~~~~~~~~~~~~~~