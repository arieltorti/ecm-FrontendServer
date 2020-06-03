# Epidemiology Compartments Modelling

## Requirements

- Python 3
- Flask
- scientific python stack (matplotlib, pandas, etc) compilation headers.

## Installing on ubuntu

```shell

$ sudo apt build-dep python3-numpy

$ python3 --version
Python 3.7.5  # 3.8 recommended

$ git clone git@github.com:maks500/CMS-FrontendServer.git

$ cd ecm-FrontendServer

$ python3 -m venv ecm-venv

$ source ecm-venv/bin/activate

(ecm-venv) $ pip install -r requirements.txt  # notice the name of the "venv" between parens.

```

## Running

```shell

$ source ecm-venv/bin/activate  # skip if already activated

$ export FLASK_APP=ecm.app

(ecm-venv) $ flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 290-409-760

```

> The included output is just an example.

## Frontend development setup

```shell
(ecm-venv) $ nodeenv -pn latest
(ecm-venv) $ npm install
(ecm-venv) $ npm run build
```

> Remember to do a build and `git add dist` before making a tag.

## Maintainers

See `MAINTANERS`.

## License

Software distributed under GPL-V3, full license text in `LICENSE`.

You can now access http://127.0.0.1:5000 and run a simulation.
