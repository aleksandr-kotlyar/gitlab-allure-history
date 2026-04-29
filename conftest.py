import pytest


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="local")


@pytest.fixture(scope="function")
def before_test(request):
    env = request.config.getoption("--env")
    print(f"before test on env {env}")
