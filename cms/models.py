import numpy as np
from scipy.integrate import odeint
from flask_sqlalchemy import SQLAlchemy
from . import schemas

db = SQLAlchemy()
class Model(db.Model):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    compartments = db.Column(db.JSON)
    params = db.Column(db.JSON)
    expressions = db.Column(db.JSON)
    reactions = db.Column(db.JSON)
    preconditions = db.Column(db.JSON)

    """
    def prepare(self, sim_data):
        schema = schemas.Model.from_orm(self)

        if sim_data.iterate:
            self.key = sim_data.iterate.get("key")
            self.start = sim_data.iterate.get("start", 0)
            self.end = sim_data.iterate.get("end", 1)
            self.intervals = sim_data.iterate.get("intervals", 10)

    def animate(self):
        for i in np.linspace(self.start, self.end, self.intervals):
            index = self.params_names.index(self.key)
            old_params = list(self.params_values)
            new_params = old_params[:]  # shallow mutable copy
            new_params[index] = i
            self.params_values = tuple(new_params)
            yield self.solve()
    """
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
