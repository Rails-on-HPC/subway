SUBWAY
========

## Howto

### Install

* `python3 setup.py install`

* or use directly by only `export SUBWAY_PATH=/abs/dir/for/bin/` (note the last `/`) and
`export PATH=$SUBWAY_PATH:$PATH`


### Simple Slurm Example

```bash
mkdir demo
cd demo
subway init
cp subway/examples/miscs/rg_main.py main.py # you may need to change shebang of this py
cp subway/examples/miscs/rg_run.py run.py
chmod +x main.py
subway config edit # add "executable": "run.py" in config.json
subway run
```


## Design principles

* Bind task to input files

* keep all input and output files, recommend uuid style filenames

* Tasks are expanded as a tree as recorded in history.json