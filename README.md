SIR Simulation Flask
====================================

Simple server to serve a frontend to the simulation engine build in Flask and VueJS.

## Requirements

> full list at `requirements.txt`.

- Python 3
- Flask
- scientific python stack (matplotlib, pandas, etc) compilation headers.

## Installing on ubuntu


```shell

$ sudo apt build-dep python3-numpy

$ python3 --version
Python 3.7.5  # 3.8 recommended

$ git clone git@github.com:maks500/CMS-FrontendServer.git

$ cd CMS-FrontendServer

$ python3 -m venv cms-venv

$ source cms-venv/bin/activate

(cms-venv) $ pip install -r requirements.txt  # notice the name of the "venv" between parens.

```

## Running

```shell

$ source cms-venv/bin/activate  # skip if already activated

(cms-venv) $ flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 290-409-760

```

> The included output is just an example.

You can now access http://127.0.0.1:5000 and run a simulation.
