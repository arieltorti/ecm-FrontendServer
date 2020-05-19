import os
import json
import pandas as pd
from werkzeug.exceptions import BadRequest
from .builder import Simulator, SimulatorError
from flask import (
    Blueprint,
    request,
    send_from_directory,
    render_template,
    Response,
    send_from_directory,
    send_file
)
from .models import Model
from . import schemas

bp = Blueprint("cms", __name__, url_prefix="/")

@bp.route("/", methods=["GET"])
def home():
    return send_file("../dist/index.html")

@bp.route("/static/<path:path>")
def serve_javascript(path):
    return send_from_directory("../dist/", path)

@bp.errorhandler(SimulatorError)
def handle_error(error):
    return {"error": error.args[1]}, 400

@bp.errorhandler(schemas.ValidationError)
def handle_error(error):
    return {"error": str(error)}, 400

@bp.route("/api/models/", methods=["GET"])
def list_models():
    models = Model.query.all()
    out = []
    for m in models:
        obj = schemas.Model.from_orm(m)
        out.append(obj.dict())
    return Response(json.dumps({"models": out}), mimetype="application/json")

@bp.route("/simulate/<int:model_id>", methods=["POST"])
def simulate(model_id):
    data = request.json
    model = Model.query.get(model_id)
    modelSchema = schemas.Model.from_orm(model)
    sim = Simulator(modelSchema)
    if not data:
        raise BadRequest(description="No input data")
    
    simulationSchema = schemas.Simulation(**data)
    response = {}

    result = sim.simulate(simulationSchema)
    if result.isIterated:
        response["type"] = "multiple"
        response["param"] = {
            "name": result.param,
            "values": list(result.paramValues)
        }
        response["frames"] = []
        for frame in result.frames:
            df = pd.DataFrame(data=frame, columns=result.compartments, index=result.timeline)
            response["frames"].append(df.transpose().to_dict(orient="split"))
    else:
        response["type"] = "simple"
        df = pd.DataFrame(data=result.frames[0], columns=result.compartments, index=result.timeline)
        response["frame"] = df.transpose().to_dict(orient="split")

    return Response(json.dumps(response), mimetype="application/json")
