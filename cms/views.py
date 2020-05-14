import os
import json
import pandas as pd
from werkzeug.exceptions import BadRequest
from .builder import Simulator

from flask import (
    Blueprint,
    request,
    send_from_directory,
    render_template,
    Response,
    send_from_directory
)
from .models import Model
from . import schemas

bp = Blueprint("cms", __name__, url_prefix="/")

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(bp.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@bp.route("/", methods=["GET"])
def home():
    models = Model.query.all()
    return render_template("index.html", models=models)

@bp.route("/js/<path:path>")
def serve_javascript(path):
    return send_from_directory("static/js", path)

@bp.route("/css/<path:path>")
def serve_styles(path):
    return send_from_directory("static/css", path)

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
    response_data = ""
    if simulationSchema.iterate:
        pass
        #response = []
        #for result in model.animate():
        #    df = pd.DataFrame(data=result, columns=model.compartments_names, index=model.tspan)
        #    response.append(df.transpose().to_dict(orient="split"))
        #response_data = json.dumps(response)
    else:
        columns, tspan, data = sim.simulate(simulationSchema)
        df = pd.DataFrame(data=data, columns=columns, index=tspan)
        response_data = df.transpose().to_json(orient="split")

    return Response(response_data, mimetype="application/json")
