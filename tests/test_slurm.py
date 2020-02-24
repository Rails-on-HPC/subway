import pytest
import sys
import os
import time
from uuid import uuid1

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.components import SlurmJob, SlurmTask

jobname = str(uuid1())


@pytest.mark.slurm
def test_task():
    t = SlurmTask(
        sbatch_path=os.path.join(os.path.dirname(__file__), "test_subway.sh"),
        sbatch_commands=["echo hello"],
        sbatch_options=["-N 1", "--job-name %s" % jobname],
    )
    t.submit()
    print(t.jobid())
    time.sleep(2)
    t.delete(include_output=True)


@pytest.mark.slurm
def test_job():
    t = SlurmJob(jobname=jobname)
    assert t.jobinfo["JobName"] == jobname
    assert t.jobinfo["State"] == "COMPLETED"
