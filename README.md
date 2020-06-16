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

(ecm-venv) $ pre-commit install  # install static analysis git hooks

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

## Contributing

See the list of pending [issues](https://github.com/maks500/ecm-FrontendServer/issues), [contributing guidelines](CONTRIBUTING.md) and contact a [maintainer](MAINTAINERS) for details abot how to contribute.

## License

Software distributed under GPL-V3, full license text in `LICENSE`.
