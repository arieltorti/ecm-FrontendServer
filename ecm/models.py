from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Model(db.Model):
    __tablename__ = "model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    compartments = db.Column(db.JSON)
    observables = db.Column(db.JSON)
    params = db.Column(db.JSON)
    expressions = db.Column(db.JSON)
    reactions = db.Column(db.JSON)
    preconditions = db.Column(db.JSON)
    template = db.Column(db.JSON, default={"groups": []})

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
