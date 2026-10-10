"""Configuration pytest : choix du mode (sil/hil) et fixtures partagées."""
from pathlib import Path

import pytest
import yaml

from bench import open_bench

ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption("--mode", default="sil", choices=["sil", "hil"],
                     help="sil = simulateur (par défaut), hil = vrai banc ESP32")
    parser.addoption("--port", default=None, help="port série de l'ESP32 (mode hil)")


@pytest.fixture(scope="session")
def limits():
    return yaml.safe_load((ROOT / "config" / "limits.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def bench(request):
    """Un seul banc ouvert pour toute la session, fermé proprement à la fin."""
    mode = request.config.getoption("--mode")
    port = request.config.getoption("--port")
    b = open_bench(mode, port)
    yield b
    b.close()
