import pytest
import os


@pytest.fixture(scope='module')
def docker_redis(docker_services):
    os.environ['PATH'] += os.pathsep + "/usr/local/bin"
    docker_services.start('redis')
