import json
import pandas as pd
from werkzeug.exceptions import BadRequest

from flask import (
    Blueprint,
    request,
    send_from_directory,
    render_template,
    Response,
)
from .models import Model
from . import schemas

bp = Blueprint("cms", __name__, url_prefix="/")


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
    return Response(json.dumps({"models": out}), mimetype="application/json",)


@bp.route("/simulate/<int:model_id>", methods=["POST"])
def simulate(model_id):
    data = request.json
    model = Model.query.get(model_id)
    if not data:
        raise BadRequest(description="No input data")

    clean_data = schemas.Simulation(**data["simulation"])
    model.prepare(clean_data)


    response_data = ""
    if clean_data.iterate:
        response = []
        for result in model.animate():
            df = pd.DataFrame(data=result, columns=model.compartments_names, index=model.tspan)
            response.append(df.transpose().to_dict(orient="split"))
        response_data = json.dumps(response)
    else:
        result = model.solve()
        df = pd.DataFrame(data=result, columns=model.compartments_names, index=model.tspan)
        response_data = df.transpose().to_json(orient="split")

    return Response(response_data, mimetype="application/json")
