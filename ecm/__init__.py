#!/usr/bin env python3
# -*- coding: utf-8 -*-

import logging
import sys

from flask import Flask
from pathlib import Path
from .views import bp
from .models import db
from .cli import load_data, create_db

BASE_DIR = Path(".")  # The folder right above this file.


def create_app():
    app = Flask(__name__, static_url_path="")
    app.register_blueprint(bp)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecm-fudepan.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["BASE_DIR"] = BASE_DIR

    app.cli.add_command(load_data)
    app.cli.add_command(create_db)

    # Configure logging.
    app.logger.setLevel(logging.DEBUG)
    del app.logger.handlers[:]

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.formatter = logging.Formatter(
        fmt=u"%(asctime)s level=%(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    app.logger.addHandler(handler)
    db.init_app(app)
    return app


app = create_app()

__all__ = ["app"]
