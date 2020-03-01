SUBWAY
========

SUBmit jobs in your own WAY.



## Install

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

Or the online doc is hosted at:

## Tests

```bash
pip install pytest
pytest
# or if you have slurm installed
pytest --slurm
```