
import json
import pytest
from pathlib import Path
import cms

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def simulation_schema():
    def inner(filename):
        data = ""
        with open(FIXTURE_DIR / filename, "r") as f:
            data = json.loads(f.read())
        return data
    return inner


@pytest.fixture
def app():
    return cms.app
