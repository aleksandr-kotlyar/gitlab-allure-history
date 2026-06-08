import random

import pytest
from allure import link

_SHOULD_FAIL = random.random() < 0.5


@link(2)
@pytest.mark.demo
def test_pass(before_test):
    assert True


@link(2)
@pytest.mark.demo
def test_fail(before_test):
    if not _SHOULD_FAIL:
        pytest.skip('flaky — пропущен')
    assert False


@link(2)
@pytest.mark.demo
def test_broken():
    if not _SHOULD_FAIL:
        return
    raise ValueError('broken')


@link(2)
@pytest.mark.demo
@pytest.mark.skip('skip')
def test_skipped():
    assert True
