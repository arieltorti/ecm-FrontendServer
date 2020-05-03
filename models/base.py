import numpy as np
import inspect

DAYS = 365
STEP = 1


class Variable:
    name = ""  # added by ModelMeta

    def __init__(self, label="", default=None, kind="int"):
        self.label = label
        self.default = default
        self.kind = kind

    def __str__(self):
        return self.name

    def __dict__(self):
        return {
            "name": self.name,
            "label": self.label,
            "default": self.default,
        }

    def __repr__(self):
        return f"{self.name}={self.default}"


class Param:
    name = ""  # added by ModelMeta

    def __init__(self, label="", default=None, kind="int"):
        self.label = label
        self.default = default
        self.kind = kind

    def __dict__(self):
        return {
            "name": self.name,
            "label": self.label,
            "default": self.default,
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}={self.default}"


class ModelMeta(type):
    def prepare_fields(meta, cls, members):
        cls.variables = []
        cls.original_params = []
        for name, value in members:
            value.name = name
            if isinstance(value, Variable):
                cls.variables.append(value)
            if isinstance(value, Param):
                cls.original_params.append(value)

    def __new__(meta, classname, bases, class_dict):
        cls = type.__new__(meta, classname, bases, class_dict)
        members = inspect.getmembers(cls, lambda o: isinstance(o, (Variable, Param)))
        meta.prepare_fields(meta, cls, members)
        cls.nb_columns = len(cls.variables)
        return cls


class Model(metaclass=ModelMeta):
    """
    Helper base class to manipulate the models without actually knowing about them.
    """
    params = ()
    variables = ()
    results = None

    def __init__(self, initial_conditions, tspan, params, days=DAYS, step=STEP):
        self.initial_conditions = initial_conditions  # must be a `Variable`s collection
        self.params = params  # Similar to `initial_conditions` with `Param`s instead
        self.tspan = tspan if tspan is not None else np.arange(0, days, step)

    def validate(self):
        """
        XXX: Must match `initial_conditions` against `self.variables`.
        XXX: must validate `params` with `self.params`
        """
        raise NotImplementedError

    @classmethod
    def available_models(cls):
        return cls.__subclasses__()

    @classmethod
    def get_model(cls, name):
        subclasses = cls.__subclasses__()
        return [x for x in subclasses if x.__name__.lower() == name].pop()

    def __dict__(self):
        """
        Only used for display purposes.
        """
        data = {
            "name": self.__class__.__name__,
        }
        data.update({x.name: x.default for x in self.variables})
        data.update({"params": [x for x in self.original_params]})
        return data

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.variables} ({self.params})"
