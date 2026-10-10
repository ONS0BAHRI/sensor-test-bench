"""Tests système T01 à T13 : la même suite tourne sur le simulateur et sur le vrai capteur.

    pytest                              -> simulateur
    pytest --mode hil --port COM3       -> vrai banc
"""
import pytest

from bench.procedures import ALL_PROCEDURES


@pytest.mark.parametrize("procedure", ALL_PROCEDURES, ids=lambda p: p.__name__)
def test_capteur(procedure, bench, limits):
    result = procedure(bench, limits)
    print(result.summary())
    assert result.passed, result.summary()
