
import json
import pytest
from pathlib import Path
from app import app as application

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sir_splitted_schema():
    data = ""
    with open(FIXTURE_DIR / "SplittedSIR.json", "r") as f:
        data = json.loads(f.read())
    return data


@pytest.fixture
def app():
    return application
