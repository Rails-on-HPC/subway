#! /bin/bash

mkdir /var/run/munge
munged -f
slurmctld
slurmd
export SUBWAY_PATH=/work/subway/bin
cd /work/subway
pytest tests --slurm -svv --cov=subway --cov-report=xml