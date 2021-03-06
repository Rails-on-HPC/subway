![SUBWAY](docs/static/subway.jpg)

<h2 align="center">SUBWAY: SUBmit jobs in your own WAY</h2>

<p align="center">
<a href="https://github.com/Rails-on-HPC/subway/actions"><img alt="Actions Status" src="https://github.com/Rails-on-HPC/subway/workflows/tests/badge.svg"></a>
<a href="https://subway.readthedocs.io"><img alt="Documentation Status" src="https://readthedocs.org/projects/subway/badge/?version=latest"></a>
<a href="https://codecov.io/gh/Rails-on-HPC/subway/"><img alt="Code Coverage" src="https://codecov.io/gh/Rails-on-HPC/subway/branch/master/graph/badge.svg"></a>
<a href="https://pypi.org/project/hpcsubway/"><img alt="Pypi version" src="https://img.shields.io/pypi/v/hpcsubway.svg"></a>
</p>


Subway is an HPC job management and automation tool. It is designed for HPC users who are tired of ``sbtach`` again and again or fail to recall the input and binary versions for given output.

By utilizing subway, the whole HPC project running from days to months can be as simple as one liner ``subway run``.


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