import numpy as np
from scipy.integrate import odeint
from flask_sqlalchemy import SQLAlchemy
from .builder import build_model
from . import schemas

db = SQLAlchemy()

DAYS = 365
STEP = 1


class Model(db.Model):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    compartments = db.Column(db.JSON)
    params = db.Column(db.JSON)
    expressions = db.Column(db.JSON)
    reactions = db.Column(db.JSON)

    def __parse_initials(self, initials, labels):
        out = ()
        if isinstance(initials, dict):
            out = tuple(initials[c] for c in labels)
        elif isinstance(initials, (list, tuple)):
            out = initials
        else:
            out = ()
        return out

    @property
    def compartments_names(self):
        return [c["name"] for c in self.compartments]

    @property
    def params_names(self):
        return tuple([p["name"] for p in self.params])

    def prepare(self, sim_data):

        schema = schemas.Model.from_orm(self)
        self.__ode_model = build_model(schema)

        self.initial_conditions = self.__parse_initials(
            sim_data.initial_conditions, self.compartments_names
        )
        breakpoint()
        self.params_values = self.__parse_initials(sim_data.params, self.params_names)
        self.tspan = np.arange(0, sim_data.days, sim_data.step)
        if sim_data.iterate:
            self.key = sim_data.iterate.get("key")
            self.start = sim_data.iterate.get("start", 0)
            self.end = sim_data.iterate.get("end", 1)
            self.step = sim_data.iterate.get("step", 1)

    def solve(self):
        res = odeint(
            self.__ode_model, self.initial_conditions,
            self.tspan, args=self.params_values,
        )
        return res

    def animate(self):
        for i in np.arange(self.start, self.stop, self.step):
            index = self.params_names.index(self.key)
            old_params = list(self.params_values)
            new_params = old_params[:]  # shallow mutable copy
            new_params[index] = i
            self.params = tuple(new_params)
            yield self.solve()

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
