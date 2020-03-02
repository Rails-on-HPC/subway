FROM python:3.6
LABEL author="refraction-ray"

RUN apt update && apt install -y slurm-wlm

RUN pip install pytest pytest-cov black

COPY docker/slurm.conf /etc/slurm-llnl/slurm.conf

COPY docker/entry.sh /work/entry.sh

COPY subway /work/subway/subway

COPY tests /work/subway/tests

COPY bin /work/subway/bin

CMD [ "/bin/bash", "-c", "source /work/entry.sh" ]