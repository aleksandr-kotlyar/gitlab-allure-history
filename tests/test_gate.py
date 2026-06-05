import pytest


@pytest.mark.smoke
def test_smoke_gate(before_test):
    assert True


@pytest.mark.regression
def test_regression_gate():
    assert 1 + 1 == 2
