#!/usr/bin env python3
# -*- coding: utf-8 -*-

import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from flask import Flask, request, send_from_directory, render_template, send_file
from werkzeug.exceptions import BadRequest
from pathlib import Path
from models import Model

HTTP_400_BAD_REQUEST = 400

BASE_PATH = Path(__file__)
STATIC_PATH = BASE_PATH / "static"
SIMULATION_ENGINE_PATH = "compartments\\compartments.exe"
SIMULATION_WD = (BASE_PATH / ".." / SIMULATION_ENGINE_PATH / "..").resolve()


app = Flask(__name__, static_url_path="")


def handle_response(inputs):
    error_dict = {}
    inputs_dict = {}

    for input_name in inputs:
        _input = request.form.get(input_name, None)
        if _input is None:
            error_dict[input_name] = f"The field {input_name} is required"
        else:
            inputs_dict[input_name] = _input

    if error_dict.keys():
        raise BadRequest(json.dumps(error_dict))
    return inputs_dict


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/js/<path:path>")
def serve_javascript(path):
    return send_from_directory("static/js", path)


@app.route("/css/<path:path>")
def serve_styles(path):
    return send_from_directory("static/css", path)


@app.route("/animate/<model_name>", methods=["POST"])
def animate(model_name):
    model = Model.get_model(model_name)

    days = request.args.get("days", default=365, type=int)
    step = request.args.get("step", default=1, type=int)
    time = np.arange(0, days, step)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")

    filepath = STATIC_PATH / f"{model_name}-{timestamp}.png"
    data = request.json
    if not data:
        raise BadRequest(description="No input data")

    breakpoint()
    results = model(**request.json).solve()
    
    S, I, R = results[:, 0], results[:, 1], results[:, 2]
    df = pd.DataFrame(data={"S": S, "I": I, "R": R}, index=time)
    df.plot()
    plt.grid(True)
    plt.savefig(filepath)
    return filepath


@app.route("/result/<string:filepath>")
def serve_result(filepath):
    return send_file(filepath, mimetype="image/png",)
