SUBWAY
========

## Howto

### Install

* `python3 setup.py install`

* or use directly by only `export SUBWAY_PATH=/abs/dir/for/bin/` (note the last `/`) and
`export PATH=$SUBWAY_PATH:$PATH` as well as `export SUBWAY_PYTHON=python of your choice`, 
default is `python3`.


### Simple Slurm Example

```bash
mkdir demo
cd demo
subway i -c subway/examples/miscs/rg_config.json
cp subway/examples/miscs/rgd_main.py main.py # you may need to change shebang of this py
cp subway/examples/miscs/rg_run.py run.py
chmod +x main.py
subway run
```

or a short cut for set up as (we recommend this way):
```bash
mkdir demo && cd demo
subway debug setup rgd
subway run
```


## Design principles

* Bind task to input files

* keep all input and output files, recommend uuid style filenames

* Tasks are expanded as a tree as recorded in history.json