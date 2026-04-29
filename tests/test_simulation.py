import pytest
from allure import link


@link(2)
@pytest.mark.demo
def test_pass(before_test):
    assert True


@link(2)
@pytest.mark.demo
def test_fail(before_test):
    assert False


@link(2)
@pytest.mark.demo
def test_broken():
    raise ValueError('broken')


@link(2)
@pytest.mark.demo
@pytest.mark.skip('skip')
def test_skipped():
    assert True
