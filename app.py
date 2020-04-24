#!/usr/bin env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, send_from_directory, render_template
from subprocess import Popen, PIPE
from pathlib import Path
import datetime
import tempfile
import json
import sys
import os

app = Flask(__name__, static_url_path='')

HTTP_400_BAD_REQUEST = 400

SIMULATION_ENGINE_PATH = "compartments\compartments.exe"
SIMULATION_WD = Path(Path(__file__).parent, SIMULATION_ENGINE_PATH).parent.resolve()


class BadRequest(Exception):
    pass

def handle_response(inputs):
    error_dict = {}
    inputs_dict = {}

    for input_name in inputs:
        _input = request.form.get(input_name, None)
        if _input is None:
            error_dict[input_name] = f'The field {input_name} is required'
        else:
            inputs_dict[input_name] = _input

    if error_dict.keys():
        raise BadRequest(json.dumps(error_dict))
    return inputs_dict

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/js/<path:path>')
def serve_javascript(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def serve_styles(path):
    return send_from_directory('static/css', path)

@app.route('/api/compute', methods=['POST'])
def simulate():
    inputs = ['config', 'model']
    try:
        inputs_dict = handle_response(inputs)

        try:
            config_file = tempfile.NamedTemporaryFile(delete=False)
            model_file = tempfile.NamedTemporaryFile(delete=False, suffix=".emodl")

            filename = f"sim-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S%f')}"

            # Configure the simulatio to output JSON results and with a unique name
            config_dict = json.loads(inputs_dict["config"])
            config_dict["output"] = {
                "prefix": f"simulations/{filename}",
                "writejson": True,
            }
            inputs_dict["config"] = json.dumps(config_dict)

            config_file.write(inputs_dict["config"].encode('utf-8'))
            model_file.write(inputs_dict["model"].encode('utf-8'))

            config_file.close()
            model_file.close()
            p = Popen([SIMULATION_ENGINE_PATH, "-m", model_file.name, "-c", config_file.name], stderr=PIPE, cwd=SIMULATION_WD)

            _, err = p.communicate()
            p.stderr.close()
            p.wait()

            if err:
                return err.decode('utf-8'), HTTP_400_BAD_REQUEST

            # Return json file, easier to parse on JS.
            return send_from_directory(Path(SIMULATION_WD, 'simulations'), filename + ".json", mimetype="application/json")
        except json.decoder.JSONDecodeError as e:
            return json.dumps({"error": "Provided JSON is invalid"}), 400

    except BadRequest as e:
        return str(e), HTTP_400_BAD_REQUEST