SUBWAY
========

SUBmit jobs in your own WAY.

![Github Action](https://github.com/Rails-on-HPC/subway/workflows/tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/subway/badge/?version=latest)](https://subway.readthedocs.io/en/latest/?badge=latest)


## Install

* `pip install hpcsubway`

* `python3 setup.py install`

* or use directly by only `export SUBWAY_PATH=/abs/dir/for/bin` and
`export PATH=$SUBWAY_PATH:$PATH` as well as `export SUBWAY_PYTHON=python of your choice`, 
default is `python3`.


## Howto

### Simple Slurm Example

Try:

```bash
mkdir demo && cd demo
subway debug setup rgd
subway run
```

## Docs

```bash
pip install sphnix
cd docs
make html
```

The generated html docs are living in ``subway/docs/_build/html``.

Or just check the online doc hosted in [readthedocs](https://subway.readthedocs.io/).

## Tests

```bash
pip install pytest
pytest
# or if you have slurm installed
pytest --slurm
```

You can also test full sets in docker if you don't have slurm configured

```bash
bash run-test.sh
```