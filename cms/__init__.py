#!/usr/bin env python3
# -*- coding: utf-8 -*-

import logging
import sys

from flask import Flask
from pathlib import Path
from .views import bp
from .models import db

HTTP_400_BAD_REQUEST = 400

BASE_PATH = Path(".")
STATIC_PATH = BASE_PATH / "static"
SIMULATION_ENGINE_PATH = "compartments\\compartments.exe"
SIMULATION_WD = (BASE_PATH / ".." / SIMULATION_ENGINE_PATH / "..").resolve()


app = Flask(__name__, static_url_path="")
app.register_blueprint(bp)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cms-fudepan.db"

db.init_app(app)

# Configure logging.
app.logger.setLevel(logging.DEBUG)
del app.logger.handlers[:]

handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
handler.formatter = logging.Formatter(
    fmt=u"%(asctime)s level=%(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ",
)
app.logger.addHandler(handler)
