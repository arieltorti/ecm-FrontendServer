#!/usr/bin env python3
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import json
from flask import Flask, request, send_from_directory, render_template, send_file
from werkzeug.exceptions import BadRequest
from pathlib import Path
from models import build_model, Model

HTTP_400_BAD_REQUEST = 400

BASE_PATH = Path(".")
STATIC_PATH = BASE_PATH / "static"
SIMULATION_ENGINE_PATH = "compartments\\compartments.exe"
SIMULATION_WD = (BASE_PATH / ".." / SIMULATION_ENGINE_PATH / "..").resolve()


app = Flask(__name__, static_url_path="")


@app.route("/", methods=["GET"])
def home():
    models = Model.available_models()
    return render_template("index.html", models=models)


@app.route("/js/<path:path>")
def serve_javascript(path):
    return send_from_directory("static/js", path)


@app.route("/css/<path:path>")
def serve_styles(path):
    return send_from_directory("static/css", path)

@app.route("/simulate/<model_name>", methods=["POST"])
def simulate(model_name):
    data = request.json
    if not data:
        raise BadRequest(description="No input data")

    model = build_model(model_name, data["model"])
    simulation = model(**data["simulation"])
    results = simulation.solve()
    return results.transpose().to_json(orient="split")

@app.route("/result/<string:filepath>")
def serve_result(filepath):
    return send_file(filepath, mimetype="image/png",)
