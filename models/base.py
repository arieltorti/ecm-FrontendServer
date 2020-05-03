import numpy as np
import inspect

DAYS = 365
STEP = 1


class ModelMeta(type):
    def __new__(meta, classname, bases, classDict):
        cls = type.__new__(meta, classname, bases, classDict)
        cls.variables = inspect.getmembers(cls, lambda o: isinstance(o, Variable))
        cls.params = inspect.getmembers(cls, lambda o: isinstance(o, Param))
        cls.nb_columns = len(cls.variables)
        return cls


class Model:
    """
    Helper base class to manipulate the models without actually knowing about them.
    """

    __metaclass__ = ModelMeta

    def __init__(self, initial_conditions, tspan, params, days=DAYS, step=STEP):
        self.index = np.arange(0, days, step)
        self.initial_conditions = initial_conditions
        self.params = params
        self.tspan = tspan

    @classmethod
    def available_models(cls):
        return cls.__subclasses__()

    @classmethod
    def get_model(cls, name):
        subclasses = cls.__subclasses__()
        return [x for x in subclasses if x.__name__.lower() == name].pop()

    def to_json():
        ...


class Variable:
    def __init__(self, name, label="", default=None, kind="int"):
        self.name = name
        self.label = label
        self.default = default
        self.kind = kind

    def __dict__(self):
        return {
            "name": self.name,
            "label": self.label,
            "default": self.default,
        }


class Param:
    def __init__(self, name, label="", default=None, kind="int"):
        self.name = name
        self.label = label
        self.default = default
        self.kind = kind

    def __dict__(self):
        return {
            "name": self.name,
            "label": self.label,
            "default": self.default,
        }