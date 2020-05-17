#!/usr/bin env python3
# -*- coding: utf-8 -*-

import json
import os
import glob
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = db.create_engine("sqlite:///cms/cms-fudepan.db")

fixture_path = "./fixture/models"

class Model(Base):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    compartments = db.Column(db.JSON)
    params = db.Column(db.JSON)
    expressions = db.Column(db.JSON)
    reactions = db.Column(db.JSON)
    preconditions = db.Column(db.JSON)

metadata = db.MetaData()

def loadModelsFixture():
    out = []
    for filename in glob.glob(os.path.join(fixture_path, '*.json')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            out.append(json.loads(f.read()))
    return out

# Create All Tables
Model.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Load table from fixture model folder
modelFixture = loadModelsFixture()

session.query(Model).delete()
session.commit()
for model in modelFixture:
    newModel = Model(**model)
    session.add(newModel)
    session.commit()
