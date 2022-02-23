import syncloudlib.integration.conftest
from os.path import dirname, join
from syncloudlib.integration.conftest import *

DIR = dirname(__file__)


@pytest.fixture(scope="session")
def project_dir():
    return join(dirname(__file__), '..')

def pytest_addoption(parser):
    syncloudlib.integration.conftest.pytest_addoption(parser)
    parser.addoption("--arch", action="store", default="unset-arch")


@pytest.fixture(scope='session')
def arch(request):
    return request.config.getoption("--arch")