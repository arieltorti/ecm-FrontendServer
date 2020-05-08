import numpy as np

DAYS = 365
STEP = 1


class Model:
    columns = ()
    results = None

    def __parse_initials(self, initials, labels):
        out = ()
        if isinstance(initials, dict):
            out = tuple(initials[c] for c in labels)
        elif isinstance(initials, (list, tuple)):
            out = initials
        else:
            out = ()
        return out

    def __init__(
        self, initial_conditions=None, params=None, tspan=None, days=DAYS, step=STEP
    ):

        self.initial_conditions = self.__parse_initials(
            initial_conditions, self.columns
        )
        self.params = self.__parse_initials(params, self.param_names)
        self.tspan = tspan if tspan is not None else np.arange(0, days, step)

    def validate(self):
        """
        XXX: Must match `initial_conditions` against `self.variables`.
        XXX: must validate `params` with `self.params`
        """
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.columns} ({self.params})"
