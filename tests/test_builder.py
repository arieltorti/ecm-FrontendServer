import pandas as pd

from pathlib import Path
from matplotlib import pyplot as plt

from cms import schemas
from cms import models


BASE_PATH = Path(__file__).parent / ".."
STATIC_PATH = BASE_PATH / "static"


def test_animate(client, simulation_schema):

    model = models.Model.query.get(5)
    result = model.animate()
    assert result
