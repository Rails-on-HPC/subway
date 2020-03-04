Plugins
========

Plain Renderer
---------------

Renderer is a type of mixin for checker class, which provide several ``_render_*`` methods.
These utilities are designed for rendering of input files and resource dict.

The main entrance is ``_render_check``. For checker class to make use of such mixin, the default implementation of ``check_checking``
and so on should follows the pattern below.

.. code-block:: python

    def check_checking(self, jobid):
        params = self.check_checking_main(jobid)
        return self._render_check(params)
    # or for kickstart
    def check_kickstart(self):
        return self._render_check(self.params)
    # or for DS scheme
    def check_finished(self, jobid):
        params = self.check_finished_main(jobid)
        return self._render_check(params=params, jobid=jobid, _type="check")


Insider ``_render_check``, the renderer is responsible for:
- generate new jobid from ``_render_newid`` (default random uuid),
- generate input files given param from ``_render_input`` (default render template with vars insider ``{}``),
- generate resource dict from ``_render_resource`` (default add ``param`` and ``job_count=1`` to resource).


Nohup
---------

The nohup like plugins are :class:`subway.plugins.nohup.NHSSub` and :class:`subway.plugins.nohup.NHSChk`.

It is worth noting, the implementation doesn't actually use ``nohup``, instead it directly use ``subprocess.Popen``
in python builtin which is non-blocking by default.



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

Specifically, :class:`subway.plugins.slurm.SlurmChk` only has slurm-specific methods for ``ending_time``, ``finishing_time``,
``is_finished``, ``is_aborted``.

For nomral user using slurm, we recommend the higher level abstraction classes which have better abstraction on job submitting and generations.

Architecture for sslurm
~~~~~~~~~~~~~~~~~~~~~~~~~

SSlurm classes are designed for SS scheme with slurm as job submission backend. SSlurm make more specific assumptions by mixin plain renderer,
and leave less code for the user to implement.

The default behavior of sslurm will automatically render input and sbatch files from templates as well as tempates pathes are
specified as ``(check_)slurm_template``, ``(check_)input_template``. All variables in the template files include ``param`` for
corresponding job, ``conf`` of subway, ``jobid`` and ``checkid`` for assoc jobs in DS scheme.

To get attributes from these dict, we use ``~`` as separator in the template and brace all variables to be rendered within ``{}``.
For example, ``{conf~inputs_abs_path}``. For list, we use key named as `list_0` and so on. For example, ``{param~size~list_1}``.

The only method, we must implement in sslurm checker, is ``check_checking_main``. It takes ``jobid`` of checking state job, and return
the params for possible new jobs. The is the core logic of how task trees grow, and such logic varies from projects which requires user customization.

More on dslurm
~~~~~~~~~~~~~~~~

DSlurm classes are designed for DS scheme. One need also to implement at least ``check_finished_main`` beyond ``check_checking_main``.
The former method should read main output and generate param for associate check job. The latter should read check output and possibly
combine with main output to generate new params for new jobs.