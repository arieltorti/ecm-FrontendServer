#!/usr/bin env python3
# -*- coding: utf-8 -*-

import json
import click

from flask import current_app
from flask.cli import with_appcontext
from ecm import db, models


def load_model_fixture(app):
    fixture_path = app.config["BASE_DIR"] / "fixture" / "models"
    for filename in fixture_path.glob("*.json"):
        out = None
        with open(filename, "r") as f:
            out = json.loads(f.read())
        yield out


@click.command()
@with_appcontext  # I hate hate hate flask's app context
def load_data():
    """
    Bootstrap command to load predefined fixtures
    """
    app = current_app

    if models.Model.query.first():
        models.Model.query.delete()

    session = db.session

    for model in load_model_fixture(app):
        instance = models.Model(**model)
        session.add(instance)
        session.commit()
        print(instance.name)


@click.command()
@with_appcontext
def create_db():
    """
    Bootstrap command to create the database if doesn't exist.
    """
    db.create_all()
