#!/usr/bin env python3
# -*- coding: utf-8 -*-

import logging
import sys
import json
from flask import (
    Flask,
    request,
    send_from_directory,
    render_template,
    send_file,
    Response,
)
from werkzeug.exceptions import BadRequest
from pathlib import Path
from models import build_model
from flask_sqlalchemy import SQLAlchemy


HTTP_400_BAD_REQUEST = 400

BASE_PATH = Path(".")
STATIC_PATH = BASE_PATH / "static"
SIMULATION_ENGINE_PATH = "compartments\\compartments.exe"
SIMULATION_WD = (BASE_PATH / ".." / SIMULATION_ENGINE_PATH / "..").resolve()


app = Flask(__name__, static_url_path="")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cms-fudepan.db"
db = SQLAlchemy(app)


class Model(db.Model):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    compartments = db.Column(db.JSON)
    params = db.Column(db.JSON)
    expressions = db.Column(db.JSON)
    reactions = db.Column(db.JSON)

    def __repr__(self):
        return "<Model %r>" % (self.name)


class Simulation(db.Model):
    __tablename__ = "simulation"
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.ForeignKey("model.id"))
    days = db.Column(db.Float)
    step = db.Column(db.Float)
    initial_conditions = db.Column(db.JSON)
    params = db.Column(db.JSON)
    iterate = db.Column(db.JSON)

    def __repr__(self):
        return "<Simuation %r>" % (self.name)


# Configure logging.
app.logger.setLevel(logging.DEBUG)
del app.logger.handlers[:]

handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
handler.formatter = logging.Formatter(
    fmt=u"%(asctime)s level=%(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ",
)
app.logger.addHandler(handler)


@app.route("/", methods=["GET"])
def home():
    models = Model.query.all()
    return render_template("index.html", models=models)


@app.route("/js/<path:path>")
def serve_javascript(path):
    return send_from_directory("static/js", path)


@app.route("/css/<path:path>")
def serve_styles(path):
    return send_from_directory("static/css", path)


@app.route("/api/models/", methods=["GET"])
def list_models():
    models = Model.query.all()
    out = []
    for m in models:
        obj = {k: v for k, v in m.__dict__.items() if not k.startswith("_")}
        out.append(obj)
    return Response(json.dumps({"models": out}), mimetype="application/json",)


@app.route("/simulate/<model_name>", methods=["POST"])
def simulate(model_name):
    data = request.json
    if not data:
        raise BadRequest(description="No input data")

    model = build_model(model_name, data["model"])
    simulation = model(**data["simulation"])
    results = simulation.solve()
    return Response(
        results.transpose().to_json(orient="split"), mimetype="application/json"
    )


@app.route("/result/<string:filepath>")
def serve_result(filepath):
    return send_file(filepath, mimetype="image/png",)
