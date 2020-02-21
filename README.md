SUBWAY
========

## Howto

### Install

`python3 setup.py install`

### usage

```bash
mkdir demo
cd demo
subway init
cp ../dev/run.py run.py
cp ../dev/main.py main.py
```

And add `"executer": "run.py"` in `demo/.subway/config.json`.

Now `subway run` again and again

## Design principles

* Bind task to input files

* keep all input and output files, recommend uuid style filenames

* Tasks are expanded as a tree as recorded in history.json